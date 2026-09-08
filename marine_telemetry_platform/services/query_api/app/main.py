from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from services.query_api.app.api.routes.telemetry import (
    router as telemetry_router,
)
from services.query_api.app.core.config import (
    get_query_api_settings,
)
from shared.database.session import (
    create_database_engine,
    create_session_factory,
)


# mesle databse engine, kafka producer ham faghat yebar sakhte mishe
# API query starts -> databse engine sakhte mishe -> session factory amade mishe -> requeste ma miad


@asynccontextmanager
async def lifespan(
    application: FastAPI,
) -> AsyncIterator[None]:
    settings = get_query_api_settings()

    engine = create_database_engine(
        settings.database_url
    )

    application.state.session_factory = (
        create_session_factory(engine)
    )

    try:
        yield
    finally:
        engine.dispose()


def create_app() -> FastAPI:
    application = FastAPI(
        title="Marine Telemetry Query API",
        version="0.1.0",
        lifespan=lifespan,
    )

    application.include_router(
        telemetry_router
    )

    return application


app = create_app()