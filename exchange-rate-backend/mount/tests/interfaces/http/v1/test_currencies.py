import pytest

from app.commons import json
from app.commons.exceptions import AppErrorCode, AppErrorMessage
from app.interfaces.http.v1.currencies import get_all_currencies


@pytest.mark.asyncio
async def test_get_all_returns_200(mock_context, mock_rates):
    mock_context.cache.get.return_value = json.dumps(mock_rates)
    resp = await get_all_currencies(ctx=mock_context)
    data = json.loads(resp.body)["data"]
    currencies = list(mock_rates.keys())
    assert resp.status_code == 200
    assert data == currencies


@pytest.mark.asyncio
async def test_get_all_returns_500(mock_context):
    mock_context.cache.get.return_value = None
    resp = await get_all_currencies(ctx=mock_context)
    data = json.loads(resp.body)["errors"][0]
    assert resp.status_code == 500
    assert data["code"] == AppErrorCode.RATES_NOT_AVAILABLE
    assert data["message"] == AppErrorMessage.RATES_NOT_AVAILABLE
