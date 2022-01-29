from asyncio.log import logger
from httpx import AsyncClient

from app.adapters.exchangerate.model import ExchangerateApiResponse
from app.commons.settings import settings
from app.commons.responses import ResponseFailure


class ExchangerateClient:

    CLIENT_NAME = "exchangerate-api"

    def __init__(self):
        self._uri = f"{settings.EXCHANGERATE_API_URL}"

    async def get_rates(self) -> ExchangerateApiResponse:
        async with AsyncClient() as client:
            resp = await client.get(
                url=f"{self._uri}/v6/latest"
            )

        body = resp.json()

        if resp.status_code >= 300:
            raise ResponseFailure(status_code=resp.status_code, response=body)

        logger.debug(body)
        return ExchangerateApiResponse.from_dict(body)
