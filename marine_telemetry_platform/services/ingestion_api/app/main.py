from fastapi import FastAPI

from services.ingestion_api.app.api.routes.health import router as health_router
from services.ingestion_api.app.api.routes.telemetry import router as telemetry_router


def create_app() -> FastAPI:
    application = FastAPI(
        title="Marine Telemetry Ingestion API",
        description="Receives telemetry batches from onboard gateways.",
        version="0.1.0",
    )

    application.include_router(health_router)
    application.include_router(telemetry_router)
    return application


app = create_app()
