import asyncio

from ..writer import Writer
from ..worker_server import WorkerServer
from app.commons.settings import settings
from .worker import Worker

from .writer import LogWriter, MetricsWriter

if __name__ == "__main__":

    Writer.register_output(LogWriter())
    Writer.register_output(MetricsWriter())

    worker = Worker()
    server = WorkerServer(worker, port=settings.SERVER_PORT)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.run())
