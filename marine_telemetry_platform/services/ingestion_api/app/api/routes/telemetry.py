from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from services.ingestion_api.app.api.dependencies import get_kafka_publisher
from services.ingestion_api.app.api.schemas.telemetry import (
    TelemetryBatchAcceptedResponse,
)
from services.ingestion_api.app.core.config import Settings, get_settings
from shared.contracts.telemetry import TelemetryBatchRequest
from shared.kafka.exceptions import KafkaPublishError
from shared.kafka.publisher import KafkaPublisher

router = APIRouter(
    prefix="/api/v1/telemetry",
    tags=["telemetry"],
)


KafkaPublisherDependency = Annotated[
    KafkaPublisher,
    Depends(get_kafka_publisher),
]

SettingsDependency = Annotated[
    Settings,
    Depends(get_settings),
]


@router.post(
    "/batches",
    response_model=TelemetryBatchAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def ingest_telemetry_batch(
    batch: TelemetryBatchRequest,
    publisher: KafkaPublisherDependency,
    settings: SettingsDependency,
) -> TelemetryBatchAcceptedResponse:
    try:
        for event in batch.events:
            publisher.enqueue(
                topic=settings.kafka_telemetry_raw_topic,
                key=event.equipment_id,
                payload=event,
            )

        publisher.flush(timeout=5.0)

    except KafkaPublishError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telemetry batch could not be published to Kafka.",
        ) from exc

    return TelemetryBatchAcceptedResponse(
        batch_id=batch.batch_id,
        accepted_events=len(batch.events),
    )
