from __future__ import annotations

from datetime import datetime

from app.models.api import FeedbackRequest, FeedbackResponse, QAAskRequest, QAAskResponse, QASummaryResponse
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
            self.logging_service.record_understanding_failure(trace_id, request.question, understanding)
            return QAAskResponse(
                request_id=trace_id,
                answer=understanding.fail_reason or "问题无法识别",
                no_data=True,
                sources=[],
                facts=[],
                status="clarify",
                code=ERROR_CODE_UNRECOGNIZED_QUESTION,
                intent=understanding.intent,
                llm_note=None,
                confidence=understanding.confidence,
                trace_id=trace_id,
            )

        if not understanding.entities:
            self.logging_service.record_entity_failure(trace_id, request.question, understanding)
            return QAAskResponse(
                request_id=trace_id,
                answer="未抽取到关键实体",
                no_data=True,
                sources=[],
                facts=[],
                status="clarify",
                code=ERROR_CODE_ENTITY_NOT_FOUND,
                intent=understanding.intent,
                llm_note=None,
                confidence=understanding.confidence,
                trace_id=trace_id,
            )

        query_plan = self.query_builder.build(understanding)
        retrieval = self.retrieval_service.retrieve(query_plan.template_name, query_plan.query_text, query_plan.parameters)
        self.logging_service.record_query(trace_id, request.question, understanding, query_plan, retrieval)

        if retrieval.status != "ok":
            return QAAskResponse(
                request_id=trace_id,
                answer="暂无相关数据",
                no_data=True,
                sources=[],
                facts=[],
                status="no_data",
                code=ERROR_CODE_NO_DATA,
                intent=understanding.intent,
                llm_note=None,
                confidence=0.0,
                trace_id=trace_id,
            )

        generated = self.answer_service.generate(understanding, retrieval, mode=request.mode)
        # Map retrieved facts and sources to SRS fields
        srs_facts = [fact.model_dump() for fact in retrieval.facts]
        srs_sources = [
            {"source_name": f.source_name, "detail_url": f.source_url} for f in retrieval.facts if f.source_name or f.source_url
        ]
        # de-duplicate sources
        unique_sources = []
        seen = set()
        for s in srs_sources:
            key = (s.get("source_name"), s.get("detail_url"))
            if key not in seen:
                seen.add(key)
                unique_sources.append(s)

        # Backward-compatible single source field for older clients/tests
        first_source = unique_sources[0] if unique_sources else None

        return QAAskResponse(
            request_id=trace_id,
            answer=generated.answer,
            no_data=False,
            sources=unique_sources,
            source=first_source,
            facts=srs_facts,
            status="ok",
            code=ERROR_CODE_SUCCESS,
            intent=understanding.intent,
            llm_note=generated.llm_note,
            confidence=generated.confidence,
            trace_id=trace_id,
        )

    def record_feedback(self, request: FeedbackRequest) -> FeedbackResponse:
        self.logging_service.record_feedback(
            FeedbackRecord(trace_id=request.trace_id, helpful=request.helpful, comment=request.comment)
        )
        return FeedbackResponse(status="ok", code=ERROR_CODE_SUCCESS, message="反馈已记录")

    def summarize_queries(self) -> QASummaryResponse:
        return QASummaryResponse(
            status="ok",
            code=ERROR_CODE_SUCCESS,
            summary=self.logging_service.summarize_queries().model_dump(),
        )

    def _trace_id(self) -> str:
        return datetime.now().strftime("t%Y%m%d_%H%M%S")