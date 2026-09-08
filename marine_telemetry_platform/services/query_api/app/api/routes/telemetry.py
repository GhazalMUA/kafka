from typing import Annotated
from datetime import datetime
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from typing import Literal
from sqlalchemy.orm import Session

from services.query_api.app.api.dependencies import (
    get_db_session,
)
from services.query_api.app.api.schemas.telemetry import (
    TelemetryMeasurementResponse,
    TelemetryAggregateResponse
)
from services.query_api.app.repositories.telemetry import (
    get_latest_measurement,
    get_measurement_history,
    get_measurement_aggregates
)

from shared.contracts.telemetry import MeasurementType
"""
GET /api/v1/equipment/{equipment_id}/latest

GET /api/v1/equipment/{equipment_id}/measurements
"""


router = APIRouter(
    prefix="/api/v1/equipment",
    tags=["telemetry"],
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db_session),
]


@router.get(
    "/{equipment_id}/latest",
    response_model=TelemetryMeasurementResponse,
)
def read_latest_measurement(
    equipment_id: str,
    session: DatabaseSession,
) -> TelemetryMeasurementResponse:
    measurement = get_latest_measurement(
        session,
        equipment_id,
    )

    if measurement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No telemetry found for this equipment.",
        )

    return TelemetryMeasurementResponse.model_validate(measurement)


@router.get(
    "/{equipment_id}/measurements",
    response_model=list[TelemetryMeasurementResponse],
)
def read_measurement_history(
    equipment_id: str,
    session: DatabaseSession,
    limit: Annotated[
        int,
        Query(ge=1, le=500),
    ] = 100,
    
    from_time: Annotated[
        datetime | None,
        Query(alias="from")
    ] = None,
    
    to_time: Annotated[
        datetime | None,
        Query(alias="to")
        ] = None,
    
    measurement_type: MeasurementType | None = None
    
) -> list[TelemetryMeasurementResponse]:
    measurements = get_measurement_history(
        session,
        equipment_id,
        limit,
        from_time,
        to_time,
        measurement_type
    )

    return [
        TelemetryMeasurementResponse.model_validate(measurement) for measurement in measurements
    ]
