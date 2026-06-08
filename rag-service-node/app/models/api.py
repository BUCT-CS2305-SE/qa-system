from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QAAskRequest(BaseModel):
    question: str = Field(..., description="用户输入的问题")
    session_id: Optional[str] = Field(default=None, description="会话标识")
    user_id: Optional[str] = Field(default=None, description="用户标识")
    mode: str = Field(default="auto", description="处理模式: auto / rule / llm")
    kg_token: Optional[str] = Field(default=None, description="KG API 用户 token（透传自前端）")


class QAAskResponse(BaseModel):
    # New SRS-aligned fields
    request_id: str
    answer: str
    no_data: bool = False
    sources: List[Dict[str, Optional[str]]] = Field(default_factory=list)
    # Backward-compatible single source for older clients/tests
    source: Optional[Dict[str, Optional[str]]] = None
    facts: List[Dict[str, Any]] = Field(default_factory=list)

    # Backward-compatible / diagnostics
    status: Optional[str] = None
    code: Optional[int] = None
    intent: Optional[str] = None
    llm_note: Optional[str] = None
    confidence: Optional[float] = None
    trace_id: Optional[str] = None


class FeedbackRequest(BaseModel):
    trace_id: str
    helpful: bool
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    status: str
    code: int
    message: str


class QASummaryResponse(BaseModel):
    status: str
    code: int
    summary: Dict[str, Any]