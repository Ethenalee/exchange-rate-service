import asyncio
from typing import List, Tuple

from app.adapters.kafka.producer import get_producer, KafkaProducerConfig, \
                                        check_producer_health
from app.commons import logger, cache
from app.commons.settings import settings
from app.commons.exceptions import AppErrorCode, AppError, AppErrorMessage
from app.usecases.poller import PollUsecases
from ..worker_server import WorkerInterface
from ..writer import Writer


class Worker(WorkerInterface):
    def __init__(self):
        self.cache_connector = cache.CacheConnector(settings.REDIS_DSN)
        self.poll_interval = settings.EXCHANGE_POLLING_TIME_IN_SECONDS

    async def connect(self) -> None:
        Writer.write(("cache", "init"))
        await self.cache_connector.connect()
        try:
            self.kafka_producer = await get_producer(
                config=KafkaProducerConfig(
                    bootstrap_servers=settings.KAFKA_SERVER,
                )
            )
        except Exception as error:
            logger.warning(error)

        await self.kafka_producer.start()
        self.cache_session = cache.CacheSession(self.cache_connector)

    async def disconnect(self) -> None:
        await self.cache_connector.close()
        await self.kafka_producer.stop()

    async def work(self) -> None:
        try:
            if settings.EXCHANGE_WORKER_PROVIDER == "exchangerate_api":
                Writer.write(("exchange_rates_poll", "poller", "start"))
                try:
                    timestamp = await PollUsecases(self.cache_session,
                                                   self.kafka_producer) \
                        ._poll_exchangerate_api_rate()
                except Exception as error:
                    logger.warning(error)
                if timestamp is not None:
                    Writer.write(("exchange_rates_poll", "poller", "end"),
                                 timestamp)
                else:
                    Writer.write(("exchange_rates_poll", "poller", "pass"))

            else:
                logger.warning(AppErrorCode.PROVIDER_NOT_AVAILALBE)
                raise AppError(AppErrorCode.PROVIDER_NOT_AVAILALBE,
                               AppErrorMessage.PROVIDER_NOT_AVAILALBE)

        except Exception as error:
            logger.warning(error)

        # Wait for next interval
        await asyncio.sleep(self.poll_interval)

    async def health_check(self) -> Tuple[bool, List[AppErrorCode]]:
        producer_healthy, cache_healthy = await asyncio.gather(
            check_producer_health(self.kafka_producer),
            self.cache_session.check_health(),
        )

        healthy = producer_healthy and cache_healthy
        failures = []

        if not producer_healthy:
            failures.append(AppErrorCode.KAFKA_PRODUCER_DISCONNECTED)
        if not cache_healthy:
            failures.append(AppErrorCode.CACHE_DISCONNECTED)

        return healthy, failures
