from confluent_kafka import Consumer

from services.storage_worker.app.core.config import StorageWorkerSettings


def build_kafka_consumer_config(
    settings: StorageWorkerSettings,
) -> dict[str, object]:
    return {
        "bootstrap.servers": settings.kafka_bootstrap_servers,
        "group.id": settings.storage_kafka_consumer_group_id,
        "client.id": settings.storage_kafka_client_id,
        "enable.auto.commit": False,  # after saving on databse we commit it by ourself
        "auto.offset.reset": "earliest",
    }


def create_kafka_consumer(
    settings: StorageWorkerSettings,
) -> Consumer:
    return Consumer(build_kafka_consumer_config(settings))
