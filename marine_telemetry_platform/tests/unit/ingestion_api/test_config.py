from services.ingestion_api.app.core.config import Settings


def test_kafka_settings_are_loaded_from_environment(monkeypatch) -> None:
    monkeypatch.setenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "test-kafka:9092",
    )
    monkeypatch.setenv(
        "KAFKA_TELEMETRY_RAW_TOPIC",
        "test.telemetry.raw.v1",
    )
    monkeypatch.setenv(
        "KAFKA_CLIENT_ID",
        "test-ingestion-api",
    )

    settings = Settings(_env_file=None)

    assert settings.kafka_bootstrap_servers == "test-kafka:9092"
    assert settings.kafka_telemetry_raw_topic == "test.telemetry.raw.v1"
    assert settings.kafka_client_id == "test-ingestion-api"
