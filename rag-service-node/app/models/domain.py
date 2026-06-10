from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EntityMention(BaseModel):
    entity_type: str
    canonical_name: str
    matched_text: str
    confidence: float


class UnderstandingResult(BaseModel):
    normalized_question: str
    intent: str
    entities: dict[str, list[EntityMention]] = Field(default_factory=dict)
    constraints: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    status: str = "ok"
    fail_reason: str | None = None


class QueryPlan(BaseModel):
    backend: str = "cypher"
    template_name: str | None = None
    query_text: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)


class RetrievedFact(BaseModel):
    subject: str
    predicate: str
    object: str
    source_name: str | None = None
    source_url: str | None = None


class RetrievalResult(BaseModel):
    status: str = "ok"
    facts: list[RetrievedFact] = Field(default_factory=list)
    raw_records: list[dict[str, Any]] = Field(default_factory=list)
    fail_reason: str | None = None


class GeneratedAnswer(BaseModel):
    answer: str
    llm_note: str | None = None
    source: list[dict[str, str]] = Field(default_factory=list)
    confidence: float = 0.0


class FeedbackRecord(BaseModel):
    trace_id: str
    helpful: bool
    comment: str | None = None


class QueryLogRecord(BaseModel):
    trace_id: str
    question: str
    normalized_question: str
    intent: str
    status: str
    confidence: float
    entities: dict[str, list[str]] = Field(default_factory=dict)
    query_text: str | None = None
    fail_reason: str | None = None


class SummaryFailureItem(BaseModel):
    trace_id: str
    question: str
    intent: str
    status: str
    fail_reason: str | None = None


class QASummary(BaseModel):
    total_questions: int = 0
    intent_distribution: dict[str, int] = Field(default_factory=dict)
    status_distribution: dict[str, int] = Field(default_factory=dict)
    average_confidence: float = 0.0
    failed_questions: list[SummaryFailureItem] = Field(default_factory=list)
