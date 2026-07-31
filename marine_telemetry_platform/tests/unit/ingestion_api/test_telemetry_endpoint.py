from uuid import uuid4

from fastapi.testclient import TestClient

from services.ingestion_api.app.main import app

client = TestClient(app)


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


def test_valid_batch_returns_202_accepted() -> None:
    """response contains which elements"""
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


def test_response_contains_number_of_accepted_events() -> None:
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


def test_batch_without_sent_at_timezone_returns_422() -> None:
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
