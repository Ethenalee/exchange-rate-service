from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel

from app.commons import json
from app.commons.cache import CacheSession
from app.commons.database import DBSession
from app.commons.exceptions import AppErrorCode
from app.repositories.exchangerate_api_rates import ExchangerateApiRateRepo


class ConvertRateResponse(BaseModel):
    base_currency: str
    quote_currency: str
    amount: Decimal


class RateUsecases:
    def __init__(self, cache: CacheSession, db: DBSession):
        self._cache = cache
        self._db = db

    async def convert_rates(
        self,
        base_currency: str,
        quote_currency: str,
        amount: Decimal,
    ) -> ConvertRateResponse:
        rates_str = await self._cache.get("rates")

        if rates_str is None:
            latest_rates = await ExchangerateApiRateRepo(self._db) \
              .get_last_rates()
            if len(latest_rates) == 0:
                return AppErrorCode.RATES_NOT_AVAILABLE
            else:
                quote_rate = list(filter(lambda x: x.currrency_code
                                  == quote_currency, latest_rates))[0].rate
                base_rate = list(filter(lambda x: x.currrency_code
                                 == base_currency, latest_rates))[0].rate
                return self._process_conversion(
                          quote_rate=quote_rate, base_rate=base_rate,
                          base_currency=base_currency,
                          quote_currency=quote_currency, amount=amount
                        )
        else:
            rates = json.loads(rates_str)
            return self._process_conversion(
              quote_rate=rates[quote_currency],
              base_rate=rates[base_currency],
              base_currency=base_currency,
              quote_currency=quote_currency, amount=amount
            )

    def _process_conversion(
        self, quote_rate: Decimal, base_rate: Decimal,
        base_currency: str, quote_currency: str, amount: Decimal
    ) -> ConvertRateResponse:
        converted_amount = Decimal(amount) * Decimal(quote_rate) \
                            / Decimal(base_rate)

        return ConvertRateResponse(
            base_currency=base_currency,
            quote_currency=quote_currency,
            amount=Decimal(converted_amount.quantize(Decimal('.01'),
                           rounding=ROUND_HALF_UP))
        )
