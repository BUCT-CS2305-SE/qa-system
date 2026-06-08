from fastapi import APIRouter, Request

from app.models.api import FeedbackRequest, FeedbackResponse, QAAskRequest, QAAskResponse, QASummaryResponse
from app.orchestration.qa_pipeline import QAPipeline


router = APIRouter(prefix="/qa", tags=["qa"])
pipeline = QAPipeline()


@router.post("/ask", response_model=QAAskResponse)
def ask_question(request: QAAskRequest, http_request: Request) -> QAAskResponse:
    kg_auth = http_request.headers.get("X-Kg-Token", "")
    if kg_auth.startswith("Bearer "):
        request.kg_token = kg_auth[7:]
    return pipeline.handle_question(request)


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(request: FeedbackRequest) -> FeedbackResponse:
    return pipeline.record_feedback(request)


@router.get("/summary", response_model=QASummaryResponse)
def query_summary() -> QASummaryResponse:
    return pipeline.summarize_queries()