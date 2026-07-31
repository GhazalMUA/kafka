from uuid import uuid4

import pytest
from pydantic import ValidationError

from shared.contracts.telemetry import (
    MeasurementType,
    MeasurementUnit,
    TelemetryBatchRequest,
    TelemetryEvent,
)


def valid_event_payload() -> dict[str, object]:
    return {
        "event_id": str(uuid4()),
        "schema_version": 1,
        "vessel_id": "vessel-001",
        "equipment_id": "thruster-port-01",
        "sensor_id": "bearing-temp-01",
        "measurement_type": "bearing_temperature",
        "value": 72.4,
        "unit": "celsius",
        "sequence_number": 1,
        "measured_at": "2026-07-31T09:30:00Z",
    }


def test_valid_telemetry_event_is_accepted() -> None:
    event = TelemetryEvent.model_validate(valid_event_payload())

    assert event.measurement_type is MeasurementType.BEARING_TEMPERATURE
    assert event.unit is MeasurementUnit.CELSIUS
    assert event.value == 72.4
    assert event.sequence_number == 1


def test_event_without_timezone_is_rejected() -> None:
    payload = valid_event_payload()
    payload["measured_at"] = "2026-07-31T09:30:00"

    with pytest.raises(ValidationError):
        TelemetryEvent.model_validate(payload)


def test_event_with_extra_field_is_rejected() -> None:
    payload = valid_event_payload()
    payload["unexpected_field"] = "unexpected-value"

    with pytest.raises(ValidationError):
        TelemetryEvent.model_validate(payload)


def test_event_with_negative_sequence_number_is_rejected() -> None:
    payload = valid_event_payload()
    payload["sequence_number"] = -1

    with pytest.raises(ValidationError):
        TelemetryEvent.model_validate(payload)


def test_empty_batch_is_rejected() -> None:
    payload = {
        "batch_id": str(uuid4()),
        "gateway_id": "gateway-vessel-001",
        "sent_at": "2026-07-31T09:31:00Z",
        "events": [],
    }

    with pytest.raises(ValidationError):
        TelemetryBatchRequest.model_validate(payload)


def test_valid_batch_is_accepted() -> None:
    payload = {
        "batch_id": str(uuid4()),
        "gateway_id": "gateway-vessel-001",
        "sent_at": "2026-07-31T09:31:00Z",
        "events": [valid_event_payload()],
    }

    batch = TelemetryBatchRequest.model_validate(payload)

    assert batch.gateway_id == "gateway-vessel-001"
    assert len(batch.events) == 1
