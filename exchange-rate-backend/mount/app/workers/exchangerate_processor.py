import asyncio
from decimal import Decimal
from json import dumps

from app.adapters.kafka.consumer import get_consumer, KafkaConsumerConfig
from app.commons import logger, cache, json, datetime_util
from app.commons.database import new_connection_pool, DBSession
from app.commons.settings import settings
from app.repositories.exchangerate_api_rates import ExchangerateApiRateRepo


class ExchangerateProcessor:
    def __init__(self):
        self.cache_connector = cache.CacheConnector(settings.REDIS_DSN)
        self.db_connector = new_connection_pool()
        self.db_session = DBSession(self.db_connector)

    async def start(self):
        self.kafka_consumer = await get_consumer(
            config=KafkaConsumerConfig(
                bootstrap_servers=settings.KAFKA_SERVER,
                consumer_group_id=settings.EXCHANGE_RATES_CONSUMER_GROUP_ID,
                topic=settings.EXCHANGE_RATES_TOPIC,
            )
        )
        await self.kafka_consumer.start()
        await self.db_connector.connect()
        await self.cache_connector.connect()
        self.cache_session = cache.CacheSession(self.cache_connector)

        logger.info("consuming kafka messages")
        try:
            async for message in self.kafka_consumer:
                if message.value:
                    logger.debug(
                        "Kafka message received",
                        kafka_topic=message.topic,
                        kafka_partition=message.partition,
                        kafka_offset=message.offset,
                        kafka_payload=dumps(message.value),
                    )
                    exchangerate_api_res = json.loads(message.value)
                    time_last_update_unix = \
                        datetime_util.timestamp_to_datetime(
                            exchangerate_api_res["time_last_update_unix"]
                        )
                    await self.cache_session.set(
                        key=settings.EXCHANGE_RATES_CACHE_KEY,
                        value=time_last_update_unix.isoformat(),
                    )

                    rates = exchangerate_api_res["rates"]
                    await self.cache_session.set(key="rates",
                                                 value=json.dumps(rates))

                    async with self.db_session.transaction():
                        for currency_code, rate in rates.items():
                            await ExchangerateApiRateRepo(self.db_session) \
                                .create(
                                currrency_code=currency_code,
                                base_currency_code=exchangerate_api_res
                                    ["base_code"],
                                rate=Decimal(rate),
                                time_last_update_unix=time_last_update_unix,
                                response=json.dumps(exchangerate_api_res),
                                )

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

    async def disconnect(self) -> None:
        await self.cache_connector.close()
        await self.db_connector.close()
        await self.kafka_consumer.stop()

    async def run(self):
        try:
            await self.start()
        except Exception as exc:
            logger.warning(exc)
        finally:
            await self.disconnect()


def main():
    loop = asyncio.get_event_loop()
    task = loop.create_task(ExchangerateProcessor().run())
    try:
        loop.run_until_complete(task)
    finally:
        loop.close()


if __name__ == "__main__":
    main()
