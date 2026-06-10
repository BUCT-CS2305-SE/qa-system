from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class QAAskRequest(BaseModel):
    question: str = Field(..., description="用户输入的问题")
    session_id: str | None = Field(default=None, description="会话标识")
    user_id: str | None = Field(default=None, description="用户标识")
    mode: str = Field(default="auto", description="处理模式: auto / rule / llm")
    kg_token: str | None = Field(default=None, description="KG API 用户 token（透传自前端）")


class QAAskResponse(BaseModel):
    # New SRS-aligned fields
    request_id: str
    answer: str
    no_data: bool = False
    sources: list[dict[str, str | None]] = Field(default_factory=list)
    # Backward-compatible single source for older clients/tests
    source: dict[str, str | None] | None = None
    facts: list[dict[str, Any]] = Field(default_factory=list)

    # Backward-compatible / diagnostics
    status: str | None = None
    code: int | None = None
    intent: str | None = None
    llm_note: str | None = None
    confidence: float | None = None
    trace_id: str | None = None


class FeedbackRequest(BaseModel):
    trace_id: str
    helpful: bool
    comment: str | None = None


class FeedbackResponse(BaseModel):
    status: str
    code: int
    message: str


class QASummaryResponse(BaseModel):
    status: str
    code: int
    summary: dict[str, Any]
