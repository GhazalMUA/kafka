from typing import Protocol

from confluent_kafka import KafkaException
from pydantic import BaseModel

from shared.kafka.exceptions import KafkaPublishError


class KafkaProducerClient(Protocol):
    """
    protocol says that each producer should contains three methods: produce(),poll(),flush()
    """

    def produce(
        self,
        topic: str,
        *,
        key: bytes | None = None,
        value: bytes | None = None,
    ) -> None: ...

    def poll(self, timeout: float) -> int: ...

    def flush(self, timeout: float | None = None) -> int: ...


class KafkaPublisher:
    """
    this is not depends on a specific class, it depends on a behavior
    """

    def __init__(self, producer: KafkaProducerClient) -> None:
        self._producer = producer

    # enqueue receives 3 things:
    # 1)message should be send to which topic
    # 2)kafka uses 'key' to send the message to a specific partition
    # 3)the pydantic model that should serialized to a json
    def enqueue(
        self,
        *,
        topic: str,
        key: str,
        payload: BaseModel,
    ) -> None:
        try:
            self._producer.produce(
                topic,
                key=key.encode("utf-8"),  # finally kafka recives key in byetes
                value=payload.model_dump_json().encode("utf-8"),
            )
            self._producer.poll(0)
        except (BufferError, KafkaException) as exc:
            raise KafkaPublishError(f"Could not enqueue message for Kafka topic '{topic}'") from exc

    def flush(self, timeout: float = 5.0) -> None:
        """handles two scenrios 1) my python producer exception 2)kafka exception"""
        try:
            remaining_messages = self._producer.flush(timeout)
        except KafkaException as exc:
            raise KafkaPublishError("Could not flush messages to Kafka") from exc

        if remaining_messages > 0:
            raise KafkaPublishError(f"{remaining_messages} Kafka message(s) were not delivered")
