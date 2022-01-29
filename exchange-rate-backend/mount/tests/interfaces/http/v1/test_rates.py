from decimal import ROUND_HALF_UP, Decimal
import pytest

from app.commons import json
from app.commons.exceptions import AppErrorCode, AppErrorMessage
from app.interfaces.http.v1.rates import convert_rates


@pytest.mark.asyncio
async def test_convert_rates_returns_200(mock_context, mock_rates):
    mock_context.cache.get.return_value = json.dumps(mock_rates)
    currencies = list(mock_rates.keys())
    base_currency = currencies[0]
    quote_currency = currencies[1]
    amount = 100

    resp = await convert_rates(
      base_currency=base_currency,
      quote_currency=quote_currency,
      amount=amount,
      ctx=mock_context)
    data = json.loads(resp.body)["data"]
    currencies = list(mock_rates.keys())
    assert resp.status_code == 200
    converted_amount = Decimal(amount) * Decimal(mock_rates[quote_currency]) \
        / Decimal(mock_rates[base_currency])

    assert data["amount"] == converted_amount.quantize(Decimal('.01'),
                                                       rounding=ROUND_HALF_UP)


@pytest.mark.asyncio
async def test_convert_rates_returns_500(mock_context, mock_rates):
    mock_context.cache.get.return_value = None
    currencies = list(mock_rates.keys())
    base_currency = currencies[0]
    quote_currency = currencies[1]
    amount = 100

    resp = await convert_rates(
      base_currency=base_currency,
      quote_currency=quote_currency,
      amount=amount,
      ctx=mock_context)

    data = json.loads(resp.body)["errors"][0]
    assert resp.status_code == 500
    assert data["code"] == AppErrorCode.RATES_NOT_AVAILABLE
    assert data["message"] == AppErrorMessage.RATES_NOT_AVAILABLE
