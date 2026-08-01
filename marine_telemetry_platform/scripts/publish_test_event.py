from datetime import UTC, datetime
from uuid import uuid4

from services.ingestion_api.app.core.config import get_settings
from services.ingestion_api.app.infrastructure.kafka import create_kafka_publisher
from shared.contracts.telemetry import TelemetryEvent


def main() -> None:
    settings = get_settings()
    publisher = create_kafka_publisher(settings)

    event = TelemetryEvent(
        event_id=uuid4(),
        schema_version=1,
        vessel_id="vessel-001",
        equipment_id="Rc2c-D_eiIo",
        sensor_id="bearing-temp-01",
        measurement_type="bearing_temperature",
        value=72.4,
        unit="celsius",
        sequence_number=1,
        measured_at=datetime.now(UTC),
    )

    publisher.enqueue(
        topic=settings.kafka_telemetry_raw_topic,
        key=event.equipment_id,
        payload=event,
    )
    publisher.flush()

    print(f"Published event {event.event_id}")


if __name__ == "__main__":
    main()
