import json
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import BaseModel

from shared.kafka.exceptions import KafkaPublishError
from shared.kafka.publisher import KafkaPublisher


class ExamplePayload(BaseModel):
    event_id: str
    measured_at: datetime


class FakeProducer:
    def __init__(self) -> None:
        self.produced_messages: list[dict[str, object]] = []
        self.poll_calls: list[float] = []
        self.remaining_messages = 0

    def produce(
        self,
        topic: str,
        *,
        key: bytes | None = None,
        value: bytes | None = None,
    ) -> None:
        self.produced_messages.append(
            {
                "topic": topic,
                "key": key,
                "value": value,
            }
        )

    def poll(self, timeout: float) -> int:
        self.poll_calls.append(timeout)
        return 0

    def flush(self, timeout: float | None = None) -> int:
        return self.remaining_messages


def test_enqueue_serializes_and_passes_message_to_producer() -> None:
    producer = FakeProducer()
    publisher = KafkaPublisher(producer)

    payload = ExamplePayload(
        event_id=str(uuid4()),
        measured_at=datetime(2026, 7, 31, 10, 30, tzinfo=UTC),
    )

    publisher.enqueue(
        topic="telemetry.raw.v1",
        key="thruster-port-01",
        payload=payload,
    )

    assert len(producer.produced_messages) == 1

    produced_message = producer.produced_messages[0]

    assert produced_message["topic"] == "telemetry.raw.v1"
    assert produced_message["key"] == b"thruster-port-01"

    decoded_value = json.loads(produced_message["value"])

    assert decoded_value["event_id"] == payload.event_id
    assert decoded_value["measured_at"] == "2026-07-31T10:30:00Z"
    assert producer.poll_calls == [0]


def test_flush_succeeds_when_all_messages_are_delivered() -> None:
    producer = FakeProducer()
    publisher = KafkaPublisher(producer)

    publisher.flush(timeout=2.0)


def test_flush_raises_error_when_messages_remain_undelivered() -> None:
    producer = FakeProducer()
    producer.remaining_messages = 2

    publisher = KafkaPublisher(producer)

    with pytest.raises(
        KafkaPublishError,
        match="2 Kafka message",
    ):
        publisher.flush(timeout=2.0)
