import unittest

from app.api.routes.health import health_check
from app.models.api import FeedbackRequest, QAAskRequest
from app.orchestration.qa_pipeline import QAPipeline


class PipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pipeline = QAPipeline()

    def test_health(self) -> None:
        payload = health_check()
        self.assertEqual(payload["status"], "ok")

    def test_ask_question_success(self) -> None:
        response = self.pipeline.handle_question(
            QAAskRequest(question="女史箴图现藏于哪家博物馆？", mode="rule")
        )
        self.assertEqual(response.status, "ok")
        self.assertEqual(response.intent, "artifact_museum")
        self.assertTrue(response.source)

    def test_ask_question_no_data(self) -> None:
        response = self.pipeline.handle_question(
            QAAskRequest(question="顾恺之的生平经历是怎样的？", mode="rule")
        )
        self.assertEqual(response.status, "no_data")

    def test_feedback(self) -> None:
        response = self.pipeline.record_feedback(
            FeedbackRequest(trace_id="t20260510_000001", helpful=True, comment="useful")
        )
        self.assertEqual(response.status, "ok")


if __name__ == "__main__":
    unittest.main()