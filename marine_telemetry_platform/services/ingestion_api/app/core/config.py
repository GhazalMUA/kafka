from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # felan faghat kafka, yani postgres ro ignore kon
    )

    kafka_bootstrap_servers: str = Field(
        default="localhost:9092",
        min_length=1,
    )
    kafka_telemetry_raw_topic: str = Field(
        default="telemetry.raw.v1",
        min_length=1,
    )
    kafka_client_id: str = Field(
        default="ingestion-api",
        min_length=1,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
