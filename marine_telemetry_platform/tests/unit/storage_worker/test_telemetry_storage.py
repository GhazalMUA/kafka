from datetime import UTC, datetime
from uuid import uuid4

from services.storage_worker.app.services.telemetry_storage import (
    build_telemetry_measurement_values,
)
from shared.contracts.telemetry import TelemetryEvent

# check for my te4lemetry storage worker.


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

    values = build_telemetry_measurement_values(event)

    assert values["event_id"] == event_id
    assert values["measured_at"] == measured_at
    assert values["schema_version"] == 1
    assert values["vessel_id"] == "vessel-001"
    assert values["equipment_id"] == "thruster-port-01"
    assert values["sensor_id"] == "bearing-temp-01"
    assert values["measurement_type"] == "bearing_temperature"
    assert values["value"] == 72.4
    assert values["unit"] == "celsius"
    assert values["sequence_number"] == 1
