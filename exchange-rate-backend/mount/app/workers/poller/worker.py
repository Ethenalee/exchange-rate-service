import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple
from dataclasses_json import dataclass_json

from app.adapters.kafka.producer import get_producer, KafkaProducerConfig, \
                                        send, check_producer_health
from app.commons import logger, cache, datetime_util
from app.commons.settings import settings
from app.commons.exceptions import AppErrorCode
from ..worker_server import WorkerInterface
from ..writer import Writer


@dataclass_json
@dataclass
class ExchangerateKey:
    provider: str
    time: datetime


class Worker(WorkerInterface):
    def __init__(self, client=None):
        self.cache_connector = cache.CacheConnector(settings.REDIS_DSN)
        self.client = client
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
            interval = self.poll_interval

            last_poll_timestamp_str = \
                await self.cache_session.get(settings.EXCHANGE_RATES_CACHE_KEY)
            last_exchangerate_api_timestamp = \
                datetime_util.fromisoformat(last_poll_timestamp_str) \
                if last_poll_timestamp_str is not None else None

            if (last_exchangerate_api_timestamp is None or
                    last_exchangerate_api_timestamp.day !=
                    datetime_util.current_date().day):
                Writer.write(("exchange_rates_poll", "poller", "start"))
                exchange_res = await self.client.get_rates()

                await send(
                    producer=self.kafka_producer,
                    topic=settings.EXCHANGE_RATES_TOPIC,
                    value=exchange_res.to_json(),
                    key=ExchangerateKey(
                            provider=settings.EXCHANGE_WORKER_PROVIDER,
                            time=exchange_res.time_last_update_unix
                            .strftime("%m_%d_%Y"))
                    .to_json()
                )
                Writer.write(("exchange_rates_poll", "poller", "end"),
                             exchange_res.time_last_update_unix
                             .strftime("%m_%d_%Y"))

        except Exception as error:
            logger.warning(error)

        # Wait for next interval
        await asyncio.sleep(interval)

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
