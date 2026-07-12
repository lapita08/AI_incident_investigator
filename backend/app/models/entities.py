from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base


def new_id() -> str:
    return str(uuid4())


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    title: Mapped[str] = mapped_column(String(240))
    description: Mapped[str] = mapped_column(Text, default="")
    severity: Mapped[str] = mapped_column(String(20), default="sev3")
    status: Mapped[str] = mapped_column(String(40), default="investigating")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    detected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    affected_services: Mapped[list[str]] = mapped_column(JSON, default=list)
    customer_impact: Mapped[str] = mapped_column(Text, default="")
    analysis_status: Mapped[str] = mapped_column(String(40), default="pending")
    analysis_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    report: Mapped[dict] = mapped_column(JSON, default=dict)
    user_conclusions: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    evidence_items: Mapped[list["EvidenceItem"]] = relationship(cascade="all, delete-orphan", back_populates="incident")
    timeline_events: Mapped[list["TimelineEvent"]] = relationship(cascade="all, delete-orphan", back_populates="incident")
    hypotheses: Mapped[list["Hypothesis"]] = relationship(cascade="all, delete-orphan", back_populates="incident")
    actions: Mapped[list["RecommendedAction"]] = relationship(cascade="all, delete-orphan", back_populates="incident")


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    display_id: Mapped[str] = mapped_column(String(40), index=True)
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id"), index=True)
    evidence_type: Mapped[str] = mapped_column(String(40))
    source: Mapped[str] = mapped_column(String(240), default="manual")
    service: Mapped[str | None] = mapped_column(String(120), nullable=True)
    environment: Mapped[str | None] = mapped_column(String(80), nullable=True)
    timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_content: Mapped[str] = mapped_column(Text)
    normalized_content: Mapped[dict] = mapped_column(JSON, default=dict)
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    ingestion_status: Mapped[str] = mapped_column(String(40), default="parsed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    incident: Mapped[Incident] = relationship(back_populates="evidence_items")


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id"), index=True)
    timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    event_type: Mapped[str] = mapped_column(String(80))
    service: Mapped[str | None] = mapped_column(String(120), nullable=True)
    title: Mapped[str] = mapped_column(String(240))
    description: Mapped[str] = mapped_column(Text, default="")
    evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    confidence: Mapped[str] = mapped_column(String(20), default="medium")
    source: Mapped[str] = mapped_column(String(120), default="deterministic")

    incident: Mapped[Incident] = relationship(back_populates="timeline_events")


class Hypothesis(Base):
    __tablename__ = "hypotheses"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id"), index=True)
    rank: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(240))
    description: Mapped[str] = mapped_column(Text)
    confidence: Mapped[str] = mapped_column(String(20), default="low")
    status: Mapped[str] = mapped_column(String(40), default="proposed")
    supporting_evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    contradicting_evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    missing_evidence: Mapped[list[str]] = mapped_column(JSON, default=list)
    validation_steps: Mapped[list[str]] = mapped_column(JSON, default=list)
    generated_by: Mapped[str] = mapped_column(String(80), default="deterministic+mock")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    incident: Mapped[Incident] = relationship(back_populates="hypotheses")
    actions: Mapped[list["RecommendedAction"]] = relationship(cascade="all, delete-orphan", back_populates="hypothesis")


class RecommendedAction(Base):
    __tablename__ = "recommended_actions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id"), index=True)
    hypothesis_id: Mapped[str | None] = mapped_column(ForeignKey("hypotheses.id"), nullable=True)
    action_type: Mapped[str] = mapped_column(String(60))
    title: Mapped[str] = mapped_column(String(240))
    description: Mapped[str] = mapped_column(Text)
    risk_level: Mapped[str] = mapped_column(String(20), default="low")
    expected_result: Mapped[str] = mapped_column(Text, default="")
    prerequisites: Mapped[list[str]] = mapped_column(JSON, default=list)
    validation: Mapped[list[str]] = mapped_column(JSON, default=list)
    rollback_considerations: Mapped[str] = mapped_column(Text, default="")
    requires_approval: Mapped[bool] = mapped_column(default=False)
    command_example: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="proposed")

    incident: Mapped[Incident] = relationship(back_populates="actions")
    hypothesis: Mapped[Hypothesis | None] = relationship(back_populates="actions")

