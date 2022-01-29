from typing import List, Union
from pydantic import BaseModel

from app.commons import json
from app.commons.cache import CacheSession
from app.commons.database import DBSession
from app.commons.exceptions import AppErrorCode
from app.repositories.exchangerate_api_rates import ExchangerateApiRateRepo


class GetCurrenciesResponse(BaseModel):
    currencies: List[str]


class CurrencyUsecases:
    def __init__(self, cache: CacheSession, db: DBSession):
        self._cache = cache
        self._db = db

    async def get_all(
        self,
    ) -> Union[GetCurrenciesResponse, AppErrorCode]:
        rates_str = await self._cache.get("rates")

        if rates_str is None:
            latest_rates = await ExchangerateApiRateRepo(self._db) \
                        .get_last_rates()
            if len(latest_rates) == 0:
                return AppErrorCode.RATES_NOT_AVAILABLE
            else:
                currencies = [
                    latest_rate.currrency_code for latest_rate in latest_rates
                ]
                return GetCurrenciesResponse(currencies=currencies)

        else:
            rates = json.loads(rates_str)
            currencies = list(rates.keys())
            return GetCurrenciesResponse(currencies=currencies)
