from decimal import Decimal
from typing import Union

from fastapi import APIRouter, Security

from app.commons import logger
from app.commons.exceptions import AppErrorCode, AppErrorMessage
from app.interfaces.http.lib.auth import no_auth
from app.interfaces.http.lib.context import RequestContext
from app.interfaces.http.lib.responses import ErrorResponse, SuccessResponse
from app.usecases.rates import RateUsecases
router = APIRouter()


@router.post("/rates", status_code=200)
async def convert_rates(
    base_currency: str,
    quote_currency: str,
    amount: Decimal,
    ctx: RequestContext = Security(no_auth),
) -> Union[SuccessResponse, ErrorResponse]:
    logger.debug("received convert rates request")
    rates_res = await RateUsecases(cache=ctx.cache, db=ctx.db) \
        .convert_rates(
            base_currency=base_currency,
            quote_currency=quote_currency,
            amount=amount
        )

    if isinstance(rates_res, AppErrorCode):
        if rates_res == AppErrorCode.RATES_NOT_AVAILABLE:
            return ErrorResponse(
                AppErrorCode.RATES_NOT_AVAILABLE,
                AppErrorMessage.RATES_NOT_AVAILABLE
            )

    return SuccessResponse(data=rates_res)
