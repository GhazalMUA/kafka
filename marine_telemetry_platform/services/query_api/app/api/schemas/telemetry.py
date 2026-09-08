from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

# in Database Model miad telemetrymeasuremnet model ro be json ghabele estefdae vaseye api tabdil mikone


class TelemetryMeasurementResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    event_id: UUID
    measured_at: datetime
    schema_version: int

    vessel_id: str
    equipment_id: str
    sensor_id: str

    measurement_type: str
    value: float
    unit: str

    sequence_number: int
    ingested_at: datetime



class TelemetryAggregateResponse(BaseModel):
    bucket_start: datetime
    avg_value: float
    min_value: float
    max_value: float
    sample_count: int