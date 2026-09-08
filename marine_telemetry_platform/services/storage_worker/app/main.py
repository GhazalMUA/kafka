from confluent_kafka import KafkaException, Message
from pydantic import ValidationError
from sqlalchemy.orm import Session, sessionmaker

from services.storage_worker.app.core.config import (
    get_storage_worker_settings,
)
from services.storage_worker.app.infrastructure.kafka import (
    create_kafka_consumer,
)
from services.storage_worker.app.services.telemetry_storage import (
    store_telemetry_event,
)
from shared.contracts.telemetry import TelemetryEvent
from shared.database.session import (
    create_database_engine,
    create_session_factory,
    session_scope,
)


def process_message(
    message: Message,
    session_factory: sessionmaker[Session],
) -> tuple[TelemetryEvent, bool]:
    payload = message.value()

    if payload is None:
        raise ValueError("Kafka message payload is empty")

    event = TelemetryEvent.model_validate_json(payload)

    with session_scope(session_factory) as session:
        was_inserted = store_telemetry_event(
            session,
            event,
        )
    return event, was_inserted


def main() -> None:
    settings = get_storage_worker_settings()

    engine = create_database_engine(settings.database_url)
    session_factory = create_session_factory(engine)
    consumer = create_kafka_consumer(settings)

    consumer.subscribe([settings.kafka_telemetry_raw_topic])

    print(f"Storage worker listening to {settings.kafka_telemetry_raw_topic}")

    try:
        while True:
            message = consumer.poll(timeout=1.0)

            if message is None:
                continue

            if message.error():
                raise KafkaException(message.error())

            try:
                event, was_inserted = process_message(
                    message,
                    session_factory,
                )

            except (ValidationError, ValueError) as exc:
                print(
                    "Skipped invalid telemetry message "
                    f"at partition {message.partition()} "
                    f"offset {message.offset()}: {exc}"
                )

                consumer.commit(
                    message=message,
                    asynchronous=False,
                )

                continue

            consumer.commit(
                message=message,
                asynchronous=False,
            )

            if was_inserted:
                print(f"Stored event {event.event_id} for equipment {event.equipment_id}")
            else:
                print(f"Skipped duplicate event {event.event_id}")

    except KeyboardInterrupt:
        print("Storage worker stopping")

    finally:
        consumer.close()
        engine.dispose()


if __name__ == "__main__":
    main()
