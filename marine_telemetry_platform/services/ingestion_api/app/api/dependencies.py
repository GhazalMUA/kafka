from fastapi import Request

from shared.kafka.publisher import KafkaPublisher


def get_kafka_publisher(request: Request) -> KafkaPublisher:
    return request.app.state.kafka_publisher
