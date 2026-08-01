from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from services.ingestion_api.app.api.dependencies import get_kafka_publisher
from services.ingestion_api.app.core.config import Settings, get_settings
from services.ingestion_api.app.main import app
from shared.kafka.exceptions import KafkaPublishError

# client = TestClient(app)


def valid_event_payload() -> dict[str, object]:
    return {
        "event_id": str(uuid4()),
        "schema_version": 1,
        "vessel_id": "vessel-001",
        "equipment_id": "thruster-port-01",
        "sensor_id": "bearing-temp-01",
        "measurement_type": "bearing_temperature",
        "value": 72.4,
        "unit": "celsius",
        "sequence_number": 1,
        "measured_at": "2026-07-31T09:30:00Z",
    }


def valid_batch_payload() -> dict[str, object]:
    return {
        "batch_id": str(uuid4()),
        "gateway_id": "gateway-vessel-001",
        "sent_at": "2026-07-31T09:31:00Z",
        "events": [valid_event_payload()],
    }


def test_response_contains_number_of_accepted_events(client: TestClient) -> None:
    """if i send 2 events, can api consider thoes 2?"""
    payload = valid_batch_payload()
    payload["events"] = [
        valid_event_payload(),
        valid_event_payload(),
    ]

    response = client.post(
        "/api/v1/telemetry/batches",
        json=payload,
    )

    assert response.status_code == 202
    assert response.json()["accepted_events"] == 2


def test_batch_without_sent_at_timezone_returns_422(client: TestClient) -> None:
    """without timezone whats happenning"""
    payload = valid_batch_payload()
    payload["sent_at"] = "2026-07-31T09:31:00"

    response = client.post(
        "/api/v1/telemetry/batches",
        json=payload,
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == [
        "body",
        "sent_at",
    ]


class FakeKafkaPublisher:
    def __init__(self) -> None:
        self.messages: list[dict[str, object]] = []
        self.flush_calls = 0
        self.fail_on_flush = False

    def enqueue(
        self,
        *,
        topic: str,
        key: str,
        payload: BaseModel,
    ) -> None:
        self.messages.append(
            {
                "topic": topic,
                "key": key,
                "payload": payload,
            }
        )

    def flush(self, timeout: float = 5.0) -> None:
        self.flush_calls += 1

        if self.fail_on_flush:
            raise KafkaPublishError("Simulated Kafka failure")


@pytest.fixture
def fake_publisher() -> FakeKafkaPublisher:
    return FakeKafkaPublisher()


@pytest.fixture
def client(
    fake_publisher: FakeKafkaPublisher,
) -> Iterator[TestClient]:
    test_settings = Settings(
        _env_file=None,
        kafka_bootstrap_servers="test-kafka:9092",
        kafka_telemetry_raw_topic="telemetry.raw.v1",
        kafka_client_id="test-ingestion-api",
    )

    app.dependency_overrides[get_kafka_publisher] = lambda: fake_publisher
    app.dependency_overrides[get_settings] = lambda: test_settings

    test_client = TestClient(app)

    yield test_client

    test_client.close()
    app.dependency_overrides.clear()


def test_valid_batch_returns_202_accepted(
    client: TestClient,
    fake_publisher: FakeKafkaPublisher,
) -> None:

    payload = valid_batch_payload()

    response = client.post(
        "/api/v1/telemetry/batches",
        json=payload,
    )

    assert response.status_code == 202
    assert response.json() == {
        "batch_id": payload["batch_id"],
        "accepted_events": 1,
        "status": "accepted",
    }

    assert len(fake_publisher.messages) == 1
    assert fake_publisher.messages[0]["topic"] == "telemetry.raw.v1"
    assert fake_publisher.messages[0]["key"] == "thruster-port-01"
    assert fake_publisher.flush_calls == 1


def test_all_batch_events_are_enqueued(
    client: TestClient,
    fake_publisher: FakeKafkaPublisher,
) -> None:
    payload = valid_batch_payload()
    payload["events"] = [
        valid_event_payload(),
        valid_event_payload(),
    ]

    response = client.post(
        "/api/v1/telemetry/batches",
        json=payload,
    )

    assert response.status_code == 202
    assert response.json()["accepted_events"] == 2

    assert len(fake_publisher.messages) == 2
    assert fake_publisher.flush_calls == 1


def test_kafka_failure_returns_503(
    client: TestClient,
    fake_publisher: FakeKafkaPublisher,
) -> None:
    fake_publisher.fail_on_flush = True

    response = client.post(
        "/api/v1/telemetry/batches",
        json=valid_batch_payload(),
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Telemetry batch could not be published to Kafka.",
    }
