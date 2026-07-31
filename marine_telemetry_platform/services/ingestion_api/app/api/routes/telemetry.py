from fastapi import APIRouter, status

from services.ingestion_api.app.api.schemas.telemetry import TelemetryBatchAcceptedResponse
from shared.contracts.telemetry import TelemetryBatchRequest

router = APIRouter(
    prefix="/api/v1/telemetry",
    tags=["telemetry"],
)


@router.post(
    "/batches",
    response_model=TelemetryBatchAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def ingest_telemetry_batch(
    batch: TelemetryBatchRequest,
) -> TelemetryBatchAcceptedResponse:
    return TelemetryBatchAcceptedResponse(
        batch_id=batch.batch_id,
        accepted_events=len(batch.events),
    )
