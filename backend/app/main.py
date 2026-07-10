from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_analysis, routes_evidence, routes_health, routes_incidents, routes_outputs
from app.core.logging import configure_logging, request_logging_middleware
from app.models.database import init_db
from app.observability.metrics import REQUEST_COUNT, REQUEST_LATENCY


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="AI Incident Investigator",
        version="0.1.0",
        description="Evidence-first incident investigation workspace for SRE teams.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def startup() -> None:
        init_db()

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        path = request.url.path
        with REQUEST_LATENCY.labels(request.method, path).time():
            response = await call_next(request)
        REQUEST_COUNT.labels(request.method, path, str(response.status_code)).inc()
        return response

    app.middleware("http")(request_logging_middleware)
    app.include_router(routes_health.router)
    app.include_router(routes_incidents.router)
    app.include_router(routes_evidence.router)
    app.include_router(routes_analysis.router)
    app.include_router(routes_outputs.router)
    return app


app = create_app()

