from decimal import Decimal
from app.commons import datetime_util, json
from app.commons.cache import CacheSession
from app.commons.database import DBSession
from app.commons.settings import settings
from app.repositories.exchangerate_api_rates import ExchangerateApiRateRepo


class ProcessorUsecases:
    def __init__(self, cache: CacheSession, db: DBSession):
        self.cache_session = cache
        self.db_session = db

    async def _process_exchangerate_api_rate(self, message):
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
