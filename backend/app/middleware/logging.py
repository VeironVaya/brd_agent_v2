import logging
import time

from fastapi import FastAPI, Request

logger = logging.getLogger("brdagent")
logging.basicConfig(level=logging.INFO)


def register_logging(app: FastAPI) -> None:
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info("%s %s -> %s (%.1fms)", request.method, request.url.path, response.status_code, duration_ms)
        return response
