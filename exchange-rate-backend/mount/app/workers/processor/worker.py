from typing import List, Tuple
import asyncio
from dataclasses import dataclass
from datetime import datetime
from dataclasses_json import dataclass_json
from json import dumps

from app.adapters.kafka.consumer import get_consumer, KafkaConsumerConfig,\
    check_consumer_health
from app.commons import logger, cache, json
from app.commons.database import new_connection_pool, DBSession, \
    do_db_health_check
from app.commons.exceptions import AppErrorCode, AppError, AppErrorMessage
from app.commons.settings import settings
from app.usecases.processor import ProcessorUsecases
from ..worker_server import WorkerInterface
from ..writer import Writer


@dataclass_json
@dataclass
class ExchangerateKey:
    provider: str
    time: datetime


class Worker(WorkerInterface):
    def __init__(self):
        self.cache_connector = cache.CacheConnector(settings.REDIS_DSN)
        self.db_connector = new_connection_pool()
        self.db_session = DBSession(self.db_connector)

    async def connect(self) -> None:
        Writer.write(("cache", "init"))
        await self.cache_connector.connect()
        try:
            self.kafka_consumer = await get_consumer(
                config=KafkaConsumerConfig(
                    bootstrap_servers=settings.KAFKA_SERVER,
                    consumer_group_id=settings
                    .EXCHANGE_RATES_CONSUMER_GROUP_ID,
                    topic=settings.EXCHANGE_RATES_TOPIC,
                )
            )
        except Exception as error:
            logger.warning(error)

        await self.kafka_consumer.start()
        await self.db_connector.connect()
        self.cache_session = cache.CacheSession(self.cache_connector)

    async def disconnect(self) -> None:
        await self.cache_connector.close()
        await self.db_connector.close()
        await self.kafka_consumer.stop()

    async def work(self) -> None:
        logger.info("consuming kafka messages")
        try:
            async for message in self.kafka_consumer:
                Writer \
                    .write(("exchange_rates_processor", "processor", "start"))
                if message.value:
                    logger.debug(
                        "Kafka message received",
                        kafka_topic=message.topic,
                        kafka_partition=message.partition,
                        kafka_offset=message.offset,
                        kafka_payload=dumps(message.value),
                    )
                    if settings.EXCHANGE_WORKER_PROVIDER == "exchangerate_api":
                        await ProcessorUsecases(self.cache_session,
                                                self.db_session) \
                            ._process_exchangerate_api_rate(message)
                        Writer \
                            .write(("exchange_rates_processor",
                                    "processor", "end"),
                                   json.loads(message.key)["time"])
                    else:
                        logger.warning(AppErrorCode.PROVIDER_NOT_AVAILALBE)
                        raise AppError(AppErrorCode.PROVIDER_NOT_AVAILALBE,
                                       AppErrorMessage.PROVIDER_NOT_AVAILALBE)

                else:
                    logger.error(
                        "KafkaError",
                        kafka_error=message.error,
                        kafka_topic=message.topic,
                        kafka_partition=message.partition,
                        kafka_offset=message.offset,
                    )
        except Exception as error:
            logger.warning(error)

    async def health_check(self) -> Tuple[bool, List[AppErrorCode]]:
        db_conncs_statuses = [
            await do_db_health_check(
                self.db_session.exec_read_one("SELECT version()"),
                "read",
            ),
            await do_db_health_check(
                self.db_session.exec_read_one("SELECT version()"),
                "write",
            ),
        ]
        db_healthy = all(db_conncs_statuses)
        consumer_healthy, cache_healthy = await asyncio.gather(
            check_consumer_health(self.kafka_consumer),
            self.cache_session.check_health(),
        )

        healthy = db_healthy and consumer_healthy and cache_healthy
        failures = []

        if not db_healthy:
            failures.append(AppErrorCode.DATABASE_UNAVAILABLE)

        if not consumer_healthy:
            failures.append(AppErrorCode.KAFKA_CONSUMER_DISCONNECTED)

        if not cache_healthy:
            failures.append(AppErrorCode.CACHE_DISCONNECTED)

        return healthy, failures
