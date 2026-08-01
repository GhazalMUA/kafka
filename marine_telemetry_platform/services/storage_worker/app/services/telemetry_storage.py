from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from shared.contracts.telemetry import TelemetryEvent
from shared.database.models import TelemetryMeasurement


# just tuen eventtelemetry(kafka) to telemetrymeasuremnet(database model)
def build_telemetry_measurement_values(
    event: TelemetryEvent,
) -> TelemetryMeasurement:
    return TelemetryMeasurement(
        event_id=event.event_id,
        measured_at=event.measured_at,
        schema_version=event.schema_version,
        vessel_id=event.vessel_id,
        equipment_id=event.equipment_id,
        sensor_id=event.sensor_id,
        measurement_type=event.measurement_type.value,
        value=event.value,
        unit=event.unit.value,
        sequence_number=event.sequence_number,
    )


def store_telemetry_event(
    session: Session,
    event: TelemetryEvent,
) -> bool:
    """it says that: insert event, based on event_id and measured_at
    if exisct, dont insert as new record, continue, dont show exception

    """
    statement = (
        insert(TelemetryMeasurement)
        .values(**build_telemetry_measurement_values(event))
        .on_conflict_do_nothing(
            index_elements=[
                "event_id",
                "measured_at",
            ]
        )
    )

    result = session.execute(statement)

    return result.rowcount == 1
