from __future__ import annotations

from datetime import datetime

from app.models.api import FeedbackRequest, FeedbackResponse, QAAskRequest, QAAskResponse
from app.models.domain import FeedbackRecord
from app.models.errors import (
    ERROR_CODE_ENTITY_NOT_FOUND,
    ERROR_CODE_NO_DATA,
    ERROR_CODE_SUCCESS,
    ERROR_CODE_UNRECOGNIZED_QUESTION,
)
from app.services.answer_generation.service import AnswerGenerationService
from app.services.input_understanding.service import InputUnderstandingService
from app.services.kg_retrieval.service import KGRetrievalService
from app.services.logging_feedback.service import LoggingFeedbackService
from app.services.query_builder.service import QueryBuilderService


class QAPipeline:
    def __init__(self) -> None:
        self.understanding_service = InputUnderstandingService()
        self.query_builder = QueryBuilderService()
        self.retrieval_service = KGRetrievalService()
        self.answer_service = AnswerGenerationService()
        self.logging_service = LoggingFeedbackService()

    def handle_question(self, request: QAAskRequest) -> QAAskResponse:
        trace_id = self._trace_id()
        understanding = self.understanding_service.understand(request.question, request.session_id)
        if understanding.status != "ok":
            return QAAskResponse(
                status="clarify",
                code=ERROR_CODE_UNRECOGNIZED_QUESTION,
                intent=understanding.intent,
                answer=understanding.fail_reason or "问题无法识别",
                facts=[],
                source=[],
                llm_note=None,
                confidence=understanding.confidence,
                trace_id=trace_id,
            )

        if not understanding.entities:
            return QAAskResponse(
                status="clarify",
                code=ERROR_CODE_ENTITY_NOT_FOUND,
                intent=understanding.intent,
                answer="未抽取到关键实体",
                facts=[],
                source=[],
                llm_note=None,
                confidence=understanding.confidence,
                trace_id=trace_id,
            )

        query_plan = self.query_builder.build(understanding)
        retrieval = self.retrieval_service.retrieve(query_plan.template_name, query_plan.query_text, query_plan.parameters)
        self.logging_service.record_query(trace_id, request.question, understanding, query_plan, retrieval)

        if retrieval.status != "ok":
            return QAAskResponse(
                status="no_data",
                code=ERROR_CODE_NO_DATA,
                intent=understanding.intent,
                answer="暂无相关数据",
                facts=[],
                source=[],
                llm_note=None,
                confidence=0.0,
                trace_id=trace_id,
            )

        generated = self.answer_service.generate(understanding, retrieval)
        return QAAskResponse(
            status="ok",
            code=ERROR_CODE_SUCCESS,
            intent=understanding.intent,
            answer=generated.answer,
            facts=[fact.model_dump() for fact in retrieval.facts],
            source=generated.source,
            llm_note=generated.llm_note,
            confidence=generated.confidence,
            trace_id=trace_id,
        )

    def record_feedback(self, request: FeedbackRequest) -> FeedbackResponse:
        self.logging_service.record_feedback(
            FeedbackRecord(trace_id=request.trace_id, helpful=request.helpful, comment=request.comment)
        )
        return FeedbackResponse(status="ok", code=ERROR_CODE_SUCCESS, message="反馈已记录")

    def _trace_id(self) -> str:
        return datetime.now().strftime("t%Y%m%d_%H%M%S")