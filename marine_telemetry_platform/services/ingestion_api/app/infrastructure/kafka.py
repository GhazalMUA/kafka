from confluent_kafka import Producer

from services.ingestion_api.app.core.config import Settings
from shared.kafka.publisher import KafkaPublisher


def build_kafka_producer_config(
    settings: Settings,
) -> dict[str, object]:
    return {
        "bootstrap.servers": settings.kafka_bootstrap_servers,
        "client.id": settings.kafka_client_id,
        "acks": "all",
        "enable.idempotence": True,
        "compression.type": "zstd",
        "linger.ms": 5,
        "delivery.timeout.ms": 30_000,
    }


def create_kafka_publisher(
    settings: Settings,
) -> KafkaPublisher:
    producer_config = build_kafka_producer_config(settings)
    producer = Producer(producer_config)

    return KafkaPublisher(producer)
