import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions import DomainError

logger = logging.getLogger("brdagent")


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        error_details = []
        for err in exc.errors():
            loc = " -> ".join(str(l) for l in err.get("loc", []))
            msg = err.get("msg", "Validation error")
            error_details.append(f"{loc}: {msg}")
        readable_message = "; ".join(error_details) if error_details else "Invalid request data."
        logger.warning(
            "Request validation error on %s %s: %s",
            request.method,
            request.url.path,
            readable_message,
        )
        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": readable_message,
                "detail": exc.errors(),
            },
        )

    @app.exception_handler(DomainError)
    async def handle_domain_error(_request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.error, "message": exc.message},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        """Catch-all for any unhandled exception.
        Returns a consistent {error, message} shape so the frontend can
        always parse the error body, and logs the full traceback so the
        cause is traceable without it leaking to the client."""
        logger.error(
            "Unhandled exception on %s %s: %s",
            request.method,
            request.url.path,
            exc,
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred. Please try again.",
            },
        )

