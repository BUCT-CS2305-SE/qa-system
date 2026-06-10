from __future__ import annotations

from collections import Counter

from app.models.domain import (
    FeedbackRecord,
    QASummary,
    QueryLogRecord,
    QueryPlan,
    RetrievalResult,
    SummaryFailureItem,
    UnderstandingResult,
)


class LoggingFeedbackService:
    def __init__(self) -> None:
        self.logs: list[QueryLogRecord] = []
        self.feedbacks: list[FeedbackRecord] = []

    def record_query(
        self,
        trace_id: str,
        question: str,
        understanding: UnderstandingResult,
        query_plan: QueryPlan,
        retrieval: RetrievalResult,
    ) -> None:
        self.logs.append(
            QueryLogRecord(
                trace_id=trace_id,
                question=question,
                normalized_question=understanding.normalized_question,
                intent=understanding.intent,
                status=retrieval.status,
                confidence=understanding.confidence,
                entities={
                    entity_type: [item.canonical_name for item in values]
                    for entity_type, values in understanding.entities.items()
                },
                query_text=query_plan.query_text,
                fail_reason=retrieval.fail_reason,
            )
        )

    def record_understanding_failure(self, trace_id: str, question: str, understanding: UnderstandingResult) -> None:
        self.logs.append(
            QueryLogRecord(
                trace_id=trace_id,
                question=question,
                normalized_question=understanding.normalized_question,
                intent=understanding.intent,
                status=understanding.status,
                confidence=understanding.confidence,
                entities={
                    entity_type: [item.canonical_name for item in values]
                    for entity_type, values in understanding.entities.items()
                },
                query_text=None,
                fail_reason=understanding.fail_reason,
            )
        )

    def record_entity_failure(self, trace_id: str, question: str, understanding: UnderstandingResult) -> None:
        self.logs.append(
            QueryLogRecord(
                trace_id=trace_id,
                question=question,
                normalized_question=understanding.normalized_question,
                intent=understanding.intent,
                status="clarify",
                confidence=understanding.confidence,
                entities={},
                query_text=None,
                fail_reason="未抽取到关键实体",
            )
        )

    def record_feedback(self, feedback: FeedbackRecord) -> None:
        self.feedbacks.append(feedback)

    def summarize_queries(self) -> QASummary:
        if not self.logs:
            return QASummary()

        intent_distribution = Counter(item.intent for item in self.logs)
        status_distribution = Counter(item.status for item in self.logs)
        average_confidence = round(sum(item.confidence for item in self.logs) / len(self.logs), 2)
        failed_questions = [
            SummaryFailureItem(
                trace_id=item.trace_id,
                question=item.question,
                intent=item.intent,
                status=item.status,
                fail_reason=item.fail_reason,
            )
            for item in self.logs
            if item.status != "ok"
        ]

        return QASummary(
            total_questions=len(self.logs),
            intent_distribution=dict(intent_distribution),
            status_distribution=dict(status_distribution),
            average_confidence=average_confidence,
            failed_questions=failed_questions,
        )
