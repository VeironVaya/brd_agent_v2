from fastapi import FastAPI

from app.middleware.cors import register_cors
from app.middleware.error_handler import register_error_handlers
from app.middleware.logging import register_logging
from app.routes import api_router

app = FastAPI(title="BRD-Agent API")

register_cors(app)
register_logging(app)
register_error_handlers(app)

app.include_router(api_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
