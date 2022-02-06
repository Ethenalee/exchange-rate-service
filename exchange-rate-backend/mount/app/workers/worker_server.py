from aiohttp import web
import asyncio
import prometheus_client
from typing import Any, Dict, List, Tuple


from app.commons.exceptions import AppErrorCode

from .writer import Writer


class WorkerInterface:
    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    async def work(self) -> None:
        pass

    @staticmethod
    async def health_check() -> Tuple[bool, List[AppErrorCode]]:
        return True, []


class WorkerServer:
    def __init__(self, worker: WorkerInterface, port: int):
        self.worker = worker
        self.port = port
        self.app = web.Application()
        self.app.router.add_routes([web.get("/health", self.health_check)])
        self.app.router.add_routes([web.get("/metrics", self.get_metrics)])
        self.worker_task = None

    async def run(self):

        try:
            await self._start_worker()
            runner = web.AppRunner(self.app)
            await runner.setup()

            site = web.TCPSite(runner, port=self.port)

            await site.start()

            await self.worker_task
        except Exception as exc:
            Writer.write(("worker_server", "exception"), exc)
        finally:
            await runner.cleanup()
            await self._stop_worker()

    async def health_check(self) -> web.Response:
        healthy, failures = await self.worker.health_check()
        response: Dict[str, Any] = {"healthy": healthy}

        if not healthy:
            response["errors"] = failures

        return web.json_response(response, status=200 if healthy else 500)

    @staticmethod
    async def get_metrics(request) -> web.Response:
        response = web.Response(body=prometheus_client.generate_latest())
        response.content_type = prometheus_client.CONTENT_TYPE_LATEST

        return response

    async def _start_worker(self):
        await self.worker.connect()
        self.worker_task = asyncio.create_task(self.worker.work())

    async def _stop_worker(self):
        if self.worker_task is not None and not self.worker_task.done():
            self.worker_task.cancel()
        await self.worker.disconnect()
