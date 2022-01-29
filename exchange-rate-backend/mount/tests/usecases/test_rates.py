from decimal import ROUND_HALF_UP, Decimal
import pytest

from app.commons import json
from app.commons.cache import CacheSession
from app.commons.database import DBSession
from app.commons.exceptions import AppErrorCode
from app.usecases.rates import RateUsecases


@pytest.mark.asyncio
async def test_convert_rates(
    cache_session: CacheSession,
    db_session: DBSession,
    mock_rates: dict[str, Decimal]
):
    rate_usecase = RateUsecases(cache_session, db_session)
    cache_session.get.return_value = json.dumps(mock_rates)
    currencies = list(mock_rates.keys())
    base_currency = currencies[0]
    quote_currency = currencies[1]
    amount = 100

    rate_res = await rate_usecase.convert_rates(
        base_currency=base_currency,
        quote_currency=quote_currency,
        amount=amount
    )
    converted_amount = Decimal(amount) * Decimal(mock_rates[quote_currency]) \
        / Decimal(mock_rates[base_currency])

    assert rate_res.amount == converted_amount.quantize(Decimal('.01'),
                                                        rounding=ROUND_HALF_UP)


@pytest.mark.asyncio
async def test_convert_rates_without_rates_data_saved(
    cache_session: CacheSession,
    db_session: DBSession,
    mock_rates: dict[str, Decimal]
):
    rate_usecase = RateUsecases(cache_session, db_session)
    cache_session.get.return_value = None

    currencies = list(mock_rates.keys())
    base_currency = currencies[0]
    quote_currency = currencies[1]
    amount = 100

    rate_res = await rate_usecase.convert_rates(
        base_currency=base_currency,
        quote_currency=quote_currency,
        amount=amount
    )

    assert rate_res == AppErrorCode.RATES_NOT_AVAILABLE
