from datetime import UTC, datetime
from uuid import uuid4

from services.storage_worker.app.services.telemetry_storage import (
    build_telemetry_measurement_values,
)
from shared.contracts.telemetry import TelemetryEvent


def test_build_telemetry_measurement_values_maps_event_fields() -> None:
    event_id = uuid4()
    measured_at = datetime.now(UTC)

    event = TelemetryEvent(
        event_id=event_id,
        schema_version=1,
        vessel_id="vessel-001",
        equipment_id="thruster-port-01",
        sensor_id="bearing-temp-01",
        measurement_type="bearing_temperature",
        value=72.4,
        unit="celsius",
        sequence_number=1,
        measured_at=measured_at,
    )

    measurement = build_telemetry_measurement_values(event)

    assert measurement.event_id == event_id
    assert measurement.measured_at == measured_at
    assert measurement.vessel_id == "vessel-001"
    assert measurement.equipment_id == "thruster-port-01"
    assert measurement.measurement_type == "bearing_temperature"
    assert measurement.value == 72.4
    assert measurement.unit == "celsius"
    assert measurement.sequence_number == 1
