'''
this is what I expect: HTTP request > 
                       TelemetryBatchRequest >
                       events: a list of (TelemetryEvent) >
                       send to Kafka in case that everything is validated



for the TelemetryEvent model =>
expected shape:
{
  "event_id": "11111111-1111-4111-8111-111111111111",
  "schema_version": 1,
  "vessel_id": "vessel-001",
  "equipment_id": "thruster-port-01",
  "sensor_id": "bearing-temp-01",
  "measurement_type": "bearing_temperature",
  "value": 72.4,
  "unit": "celsius",
  "sequence_number": 1,
  "measured_at": "2026-07-31T09:30:00Z"
}

for the TelemetryBatchRequest model =>
expected shape:
{
  "batch_id": "22222222-2222-4222-8222-222222222222",
  "gateway_id": "gateway-vessel-001",
  "sent_at": "2026-07-31T09:31:00Z",
  "events": [
    {
      "event_id": "11111111-1111-4111-8111-111111111111",
      "schema_version": 1,
      "vessel_id": "vessel-001",
      "equipment_id": "thruster-port-01",
      "sensor_id": "bearing-temp-01",
      "measurement_type": "bearing_temperature",
      "value": 72.4,
      "unit": "celsius",
      "sequence_number": 1,
      "measured_at": "2026-07-31T09:30:00Z"
    }
  ]
}

'''


from pydantic import BaseModel, ConfigDict, Field, field_validator

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID


# same law for identifiers
Identifier = Annotated[
  str,
  Field(
    min_length = 1,
    max_length = 100,
    pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$",
  ),
]


# list of valid measurment items
class MeasurementType(StrEnum):
    BEARING_TEMPERATURE = "bearing_temperature"
    VIBRATION = "vibration"
    PRESSURE = "pressure"
    RPM = "rpm"
    
    
# list of valid units
class MeasurementUnit(StrEnum):
    CELSIUS = "celsius"
    MILLIMETERS_PER_SECOND = "mm_s"
    BAR = "bar"
    REVOLUTIONS_PER_MINUTE = "rpm"


# same models settings, cant accept extra undefiend term and dont concider first and last space
class ContractModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",    # it helps us when producer sends unknown fileds, event skip it
        str_strip_whitespace=True,
    )

# contract of a sensor measurment    
class TelemetryEvent(ContractModel):
    event_id: UUID
    schema_version: Literal[1]   # for example after 2 month we add oil condition or angle, on that time we add schema v2 

    vessel_id: Identifier   # standard formation of id
    equipment_id: Identifier  # standard formation of id
    sensor_id: Identifier   # standard formation of id

    measurement_type: MeasurementType   # only defiend terms can be measured
    value: float = Field(allow_inf_nan=False)  # it doesnt accept infinity, -infinity, nan
    unit: MeasurementUnit    # valid unites we defiend

    sequence_number: int = Field(ge=0)    # should be greater than 0 and cant be negative
    measured_at: datetime

    @field_validator("measured_at")
    @classmethod
    def measured_at_must_include_timezone(cls, value: datetime) -> datetime:
      '''
        if it doesnt have timezone we dont know the time is based on tehran or amsterdam or utc or ...
      '''
      
      if value.tzinfo is None or value.utcoffset() is None:
          raise ValueError("measured_at must include a timezone")

      return value    
      
# shows that each event should contains how many batches
class TelemetryBatchRequest(ContractModel):
    batch_id: UUID
    gateway_id: Identifier
    sent_at: datetime

    events: list[TelemetryEvent] = Field(
        min_length=1,
        max_length=500,     # i want to concider it as 500 at first, but after load test we may should change it.
    )

    @field_validator("sent_at")
    @classmethod
    def sent_at_must_include_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("sent_at must include a timezone")

        return value      