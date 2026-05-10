from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EntityMention(BaseModel):
    entity_type: str
    canonical_name: str
    matched_text: str
    confidence: float


class UnderstandingResult(BaseModel):
    normalized_question: str
    intent: str
    entities: Dict[str, List[EntityMention]] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    status: str = "ok"
    fail_reason: Optional[str] = None


class QueryPlan(BaseModel):
    backend: str = "cypher"
    template_name: Optional[str] = None
    query_text: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class RetrievedFact(BaseModel):
    subject: str
    predicate: str
    object: str
    source_name: Optional[str] = None
    source_url: Optional[str] = None


class RetrievalResult(BaseModel):
    status: str = "ok"
    facts: List[RetrievedFact] = Field(default_factory=list)
    raw_records: List[Dict[str, Any]] = Field(default_factory=list)
    fail_reason: Optional[str] = None


class GeneratedAnswer(BaseModel):
    answer: str
    llm_note: Optional[str] = None
    source: List[Dict[str, str]] = Field(default_factory=list)
    confidence: float = 0.0


class FeedbackRecord(BaseModel):
    trace_id: str
    helpful: bool
    comment: Optional[str] = None