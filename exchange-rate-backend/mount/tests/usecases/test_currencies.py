from decimal import Decimal
import pytest

from app.commons import json
from app.commons.cache import CacheSession
from app.commons.database import DBSession
from app.commons.exceptions import AppErrorCode
from app.usecases.currencies import CurrencyUsecases


@pytest.mark.asyncio
async def test_get_all(
    cache_session: CacheSession,
    db_session: DBSession,
    mock_rates: dict[str, Decimal]
):
    currency_usecase = CurrencyUsecases(cache_session, db_session)
    cache_session.get.return_value = json.dumps(mock_rates)

    currencies_res = await currency_usecase.get_all()

    assert currencies_res.currencies == list(mock_rates.keys())


@pytest.mark.asyncio
async def test_get_all_without_rates_data_saved(
    cache_session: CacheSession,
    db_session: DBSession,
):
    currency_usecase = CurrencyUsecases(cache_session, db_session)
    cache_session.get.return_value = None

    currencies_res = await currency_usecase.get_all()

    assert currencies_res == AppErrorCode.RATES_NOT_AVAILABLE
