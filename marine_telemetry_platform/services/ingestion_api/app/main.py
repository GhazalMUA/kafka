from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from services.ingestion_api.app.api.routes.health import router as health_router
from services.ingestion_api.app.api.routes.telemetry import router as telemetry_router
from services.ingestion_api.app.core.config import get_settings
from services.ingestion_api.app.infrastructure.kafka import create_kafka_publisher


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    publisher = create_kafka_publisher(settings)

    application.state.kafka_publisher = publisher

    try:
        yield
    finally:
        publisher.flush(timeout=10.0)


def create_app() -> FastAPI:
    application = FastAPI(
        title="Marine Telemetry Ingestion API",
        description="Receives telemetry batches from onboard gateways.",
        version="0.1.0",
        lifespan=lifespan,
    )

    application.include_router(health_router)
    application.include_router(telemetry_router)
    return application


app = create_app()
