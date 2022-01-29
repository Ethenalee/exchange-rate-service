from typing import Optional

import asyncio
from aiokafka import AIOKafkaConsumer, ConsumerRecord
from kafka.structs import TopicPartition

from app.adapters.kafka.kafka_config import KafkaConsumerConfig
from app.commons import logger, json


async def consume(
    consumer: AIOKafkaConsumer,
):
    async for message in consumer:
        if message.value:
            logger.debug(
                "Kafka message received",
                kafka_topic=message.topic,
                kafka_partition=message.partition,
                kafka_offset=message.offset,
                kafka_payload=json.dumps(message.value),
            )
            yield message
        else:
            logger.error(
                "KafkaError",
                kafka_error=message.error,
                kafka_topic=message.topic,
                kafka_partition=message.partition,
                kafka_offset=message.offset,
            )


async def get_consumer(
    config: KafkaConsumerConfig,
) -> AIOKafkaConsumer:
    def _json_deserializer(rec: Optional[bytes]):
        return json.loads(rec.decode()) if rec else None

    return AIOKafkaConsumer(
        config.topic,
        bootstrap_servers=config.bootstrap_servers,
        group_id=config.consumer_group_id,
        loop=asyncio.get_event_loop(),
        key_deserializer=_json_deserializer,
        value_deserializer=_json_deserializer,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )


def _get_offsets_map(rec: ConsumerRecord) -> dict[TopicPartition, int]:
    return {TopicPartition(rec.topic, rec.partition): rec.offset + 1}


async def check_consumer_health(consumer: AIOKafkaConsumer) -> bool:
    partitions = consumer.assignment()

    if not partitions:
        return False

    return True
