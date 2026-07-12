from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.observability.metrics import prometheus_payload

router = APIRouter(tags=["health"])


@router.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
def ready(db: Session = Depends(db_session)) -> dict[str, str]:
    db.execute(text("select 1"))
    return {"status": "ready"}


@router.get("/metrics")
def metrics() -> Response:
    return Response(content=prometheus_payload(), media_type="text/plain; version=0.0.4")
