from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QAAskRequest(BaseModel):
    question: str = Field(..., description="用户输入的问题")
    session_id: Optional[str] = Field(default=None, description="会话标识")
    user_id: Optional[str] = Field(default=None, description="用户标识")
    mode: str = Field(default="auto", description="处理模式: auto / rule / llm")


class QAAskResponse(BaseModel):
    status: str
    code: int
    intent: str
    answer: str
    facts: List[Dict[str, Any]] = Field(default_factory=list)
    source: List[Dict[str, str]] = Field(default_factory=list)
    llm_note: Optional[str] = None
    confidence: float = 0.0
    trace_id: str


class FeedbackRequest(BaseModel):
    trace_id: str
    helpful: bool
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    status: str
    code: int
    message: str