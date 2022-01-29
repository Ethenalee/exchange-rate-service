import asyncio
from dataclasses import dataclass
from datetime import datetime
from dataclasses_json import dataclass_json

from app.adapters.exchangerate.client import ExchangerateClient
from app.adapters.kafka.producer import get_producer, KafkaProducerConfig, send
from app.commons import logger, cache, datetime_util
from app.commons.settings import settings


@dataclass_json
@dataclass
class ExchangerateKey:
    provider: str
    time: datetime


class ExchangeratePoller():
    def __init__(self):
        self.cache_connector = cache.CacheConnector(settings.REDIS_DSN)

    async def start(self):
        self.kafka_producer = await get_producer(
                config=KafkaProducerConfig(
                    bootstrap_servers=settings.KAFKA_SERVER,
                )
            )

        await self.kafka_producer.start()

        await self.cache_connector.connect()
        self.cache_session = cache.CacheSession(self.cache_connector)

        exchangerate_client = ExchangerateClient()

        interval = settings.EXCHANGE_POLLING_TIME_IN_SECONDS

        last_exchangerate_api_timestamp_str = \
            await self.cache_session.get(settings.EXCHANGE_RATES_CACHE_KEY)
        last_exchangerate_api_timestamp = \
            datetime_util.fromisoformat(last_exchangerate_api_timestamp_str) \
            if last_exchangerate_api_timestamp_str is not None else None

        if (last_exchangerate_api_timestamp is None or
                last_exchangerate_api_timestamp.day !=
                datetime_util.current_date().day):
            exchange_res = await exchangerate_client.get_rates()

            await send(
                producer=self.kafka_producer,
                topic=settings.EXCHANGE_RATES_TOPIC,
                value=exchange_res.to_json(),
                key=ExchangerateKey(provider="exchangerate_api",
                                    time=exchange_res.time_last_update_unix)
                .to_json()
            )
        # Wait for next interval
        await asyncio.sleep(interval)

    async def disconnect(self) -> None:
        await self.cache_connector.close()
        await self.kafka_producer.stop()

    async def run(self):
        try:
            await self.start()
        except Exception as exc:
            logger.warning(exc)
        finally:
            await self.disconnect()


def main():
    loop = asyncio.get_event_loop()
    task = loop.create_task(ExchangeratePoller().run())
    try:
        loop.run_until_complete(task)
    finally:
        loop.close()


if __name__ == "__main__":
    main()
