from sqlalchemy import text

from services.ingestion_api.app.core.config import get_settings
from shared.database.session import create_database_engine


def main() -> None:
    settings = get_settings()
    engine = create_database_engine(settings.database_url)

    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT
                    current_database(),
                    current_user,
                    extversion
                FROM pg_extension
                WHERE extname = 'timescaledb'
                """
            )
        ).one()

    print(f"Database: {result[0]}")
    print(f"User: {result[1]}")
    print(f"TimescaleDB: {result[2]}")

    engine.dispose()


if __name__ == "__main__":
    main()