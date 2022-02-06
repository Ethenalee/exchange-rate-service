import asyncio

from app.adapters.exchangerate.client import ExchangerateClient
from app.commons.settings import settings
from ..writer import Writer
from ..worker_server import WorkerServer
from .worker import Worker

from .writer import LogWriter, MetricsWriter

if __name__ == "__main__":

    Writer.register_output(LogWriter())
    Writer.register_output(MetricsWriter())

    def _get_client():
        if settings.EXCHANGE_WORKER_PROVIDER == "exchangerate_api":
            return ExchangerateClient()

    worker = Worker(_get_client())
    server = WorkerServer(worker, port=settings.SERVER_PORT)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.run())
