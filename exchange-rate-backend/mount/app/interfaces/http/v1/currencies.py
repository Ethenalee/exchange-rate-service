from typing import Union
from fastapi import APIRouter, Security

from app.commons import logger
from app.commons.exceptions import AppErrorCode, AppErrorMessage
from app.interfaces.http.lib.auth import no_auth
from app.interfaces.http.lib.context import RequestContext
from app.interfaces.http.lib.responses import ErrorResponse, SuccessResponse
from app.usecases.currencies import CurrencyUsecases

router = APIRouter()


@router.get("/currencies", status_code=200,
            )
async def get_all_currencies(
    ctx: RequestContext = Security(no_auth),
) -> Union[SuccessResponse, ErrorResponse]:
    logger.debug("received get currencies request")

    currencies_res = await CurrencyUsecases(cache=ctx.cache, db=ctx.db) \
        .get_all()

    if isinstance(currencies_res, AppErrorCode):
        if currencies_res == AppErrorCode.RATES_NOT_AVAILABLE:
            return ErrorResponse(
                AppErrorCode.RATES_NOT_AVAILABLE,
                AppErrorMessage.RATES_NOT_AVAILABLE
            )

    return SuccessResponse(data=currencies_res.currencies)
