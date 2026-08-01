from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageWorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    kafka_bootstrap_servers: str = Field(
        default="localhost:9092",
        min_length=1,
    )

    kafka_telemetry_raw_topic: str = Field(
        default="telemetry.raw.v1",
        min_length=1,
    )

    storage_kafka_consumer_group_id: str = Field(
        default="storage-worker-v1",
        min_length=1,
    )

    storage_kafka_client_id: str = Field(
        default="storage-worker",
        min_length=1,
    )

    database_url: str = Field(min_length=1)


@lru_cache
def get_storage_worker_settings() -> StorageWorkerSettings:
    return StorageWorkerSettings()
