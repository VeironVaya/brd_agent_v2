import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.middleware.cors import register_cors
from app.middleware.error_handler import register_error_handlers
from app.middleware.logging import register_logging
from app.repositories import revoked_token_repository
from app.routes import api_router

logger = logging.getLogger("brdagent")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Startup tasks that run once before the first request:
    - Purge expired revoked tokens so the denylist never grows unboundedly.
    """
    async with SessionLocal() as session:
        deleted = await revoked_token_repository.delete_expired(session)
        await session.commit()
    if deleted:
        logger.info("Purged %d expired revoked token(s) on startup", deleted)
    yield  # app runs here


app = FastAPI(title="BRD-Agent API", lifespan=lifespan)

register_cors(app)
register_logging(app)
register_error_handlers(app)

app.include_router(api_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

