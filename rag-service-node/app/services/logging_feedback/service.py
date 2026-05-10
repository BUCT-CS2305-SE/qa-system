from __future__ import annotations

from typing import Dict, List

from app.models.domain import FeedbackRecord, QueryPlan, RetrievalResult, UnderstandingResult


class LoggingFeedbackService:
    def __init__(self) -> None:
        self.logs: List[Dict[str, object]] = []
        self.feedbacks: List[FeedbackRecord] = []

    def record_query(
        self,
        trace_id: str,
        question: str,
        understanding: UnderstandingResult,
        query_plan: QueryPlan,
        retrieval: RetrievalResult,
    ) -> None:
        self.logs.append(
            {
                "trace_id": trace_id,
                "question": question,
                "intent": understanding.intent,
                "entities": understanding.entities,
                "query_text": query_plan.query_text,
                "result_status": retrieval.status,
            }
        )

    def record_feedback(self, feedback: FeedbackRecord) -> None:
        self.feedbacks.append(feedback)