from datetime import datetime
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from aiokafka import AIOKafkaProducer

from app.adapters.exchangerate.client import ExchangerateClient
from app.adapters.kafka.producer import send
from app.commons import datetime_util
from app.commons.cache import CacheSession
from app.commons.settings import settings


@dataclass_json
@dataclass
class ExchangerateKey:
    provider: str
    time: datetime


class PollUsecases:
    def __init__(self, cache: CacheSession,
                 kafka_producer: AIOKafkaProducer):
        self.cache_session = cache
        self.kafka_producer = kafka_producer

    async def _poll_exchangerate_api_rate(self):
        client = ExchangerateClient()
        last_poll_timestamp_str = \
            await self.cache_session.get(settings.EXCHANGE_RATES_CACHE_KEY)
        last_exchangerate_api_timestamp = \
            datetime_util.fromisoformat(last_poll_timestamp_str) \
            if last_poll_timestamp_str is not None else None

        if (last_exchangerate_api_timestamp is None or
                last_exchangerate_api_timestamp.day !=
                datetime_util.current_date().day):
            exchange_res = await client.get_rates()

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

            return exchange_res.time_last_update_unix.strftime("%m_%d_%Y")
