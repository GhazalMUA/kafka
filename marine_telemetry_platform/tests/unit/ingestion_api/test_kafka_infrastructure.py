from services.ingestion_api.app.core.config import Settings
from services.ingestion_api.app.infrastructure.kafka import build_kafka_producer_config


def test_build_kafka_producer_config() -> None:
    settings = Settings(
        _env_file=None,
        kafka_bootstrap_servers="test-kafka:9092",
        kafka_telemetry_raw_topic="test.telemetry.raw.v1",
        kafka_client_id="test-ingestion-api",
    )

    config = build_kafka_producer_config(settings)

    assert config == {
        "bootstrap.servers": "test-kafka:9092",
        "client.id": "test-ingestion-api",
        "acks": "all",
        "enable.idempotence": True,
        "compression.type": "zstd",
        "linger.ms": 5,
        "delivery.timeout.ms": 30_000,
    }
