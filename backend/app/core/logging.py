import logging
import sys
from collections.abc import Callable
from contextvars import ContextVar
from time import perf_counter

from fastapi import Request, Response
from pythonjsonlogger import jsonlogger

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s")
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)


async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    request_id = request.headers.get("x-request-id", request.scope.get("trace_id", "-"))
    token = request_id_ctx.set(str(request_id))
    started = perf_counter()
    try:
        response = await call_next(request)
        duration_ms = round((perf_counter() - started) * 1000, 2)
        logging.getLogger("app.request").info(
            "request completed",
            extra={
                "request_id": request_id,
                "operation": f"{request.method} {request.url.path}",
                "duration_ms": duration_ms,
                "status": response.status_code,
            },
        )
        response.headers["x-request-id"] = str(request_id)
        return response
    finally:
        request_id_ctx.reset(token)

