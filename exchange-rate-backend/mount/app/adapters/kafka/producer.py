from typing import Optional
import asyncio
from aiokafka import AIOKafkaProducer

from app.adapters.kafka.kafka_config import KafkaProducerConfig
from app.commons import logger, json


async def send(
    producer: AIOKafkaProducer,
    topic: str,
    value: Optional[object] = None,
    key: Optional[object] = None,
):

    logger.debug(
        "Producing Kafka message",
        kafka_topic=topic,
        kafka_value=json.dumps(value),
        kafka_key=json.dumps(key),
    )
    await producer.send_and_wait(
        topic=topic,
        key=key,
        value=value,
    )
    logger.debug("Produced Kafka message")


async def get_producer(config: KafkaProducerConfig) -> AIOKafkaProducer:
    def _json_serializer(v):
        return json.dumps(v).encode()

    return AIOKafkaProducer(
        bootstrap_servers=config.bootstrap_servers,
        loop=asyncio.get_event_loop(),
        key_serializer=_json_serializer,
        value_serializer=_json_serializer,
    )


async def check_producer_health(producer: AIOKafkaProducer) -> bool:
    brokers = producer.client.cluster.brokers()

    if not brokers:
        return False

    for broker in brokers:
        if not await producer.client.ready(broker.nodeId):
            return False

    return True
