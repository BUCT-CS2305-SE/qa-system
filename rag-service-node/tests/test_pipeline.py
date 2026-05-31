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

    def test_artifact_museum(self) -> None:
        response = self.pipeline.handle_question(
            QAAskRequest(question="Admonitions Scroll museum?", mode="rule")
        )
        self.assertEqual(response.status, "ok")
        self.assertEqual(response.intent, "artifact_museum")

    def test_artist_biography_success(self) -> None:
        response = self.pipeline.handle_question(
            QAAskRequest(question="Zhang Zeduan biography?", mode="rule")
        )
        self.assertEqual(response.status, "ok")
        self.assertEqual(response.intent, "artist_biography")

    def test_unknown_question_clarify(self) -> None:
        response = self.pipeline.handle_question(
            QAAskRequest(question="blah blah?", mode="rule")
        )
        self.assertEqual(response.status, "clarify")

    def test_feedback(self) -> None:
        response = self.pipeline.record_feedback(
            FeedbackRequest(trace_id="t20260510_000001", helpful=True, comment="useful")
        )
        self.assertEqual(response.status, "ok")

    def test_artifact_type(self) -> None:
        response = self.pipeline.handle_question(
            QAAskRequest(question="Tea Bowl and Dish type?", mode="rule")
        )
        self.assertEqual(response.status, "ok")
        self.assertEqual(response.intent, "artifact_type")

    def test_artifact_material(self) -> None:
        response = self.pipeline.handle_question(
            QAAskRequest(question="Bronze Galloping Horse material?", mode="rule")
        )
        self.assertEqual(response.status, "ok")
        self.assertEqual(response.intent, "artifact_material")

    def test_artifact_description(self) -> None:
        response = self.pipeline.handle_question(
            QAAskRequest(question="Tea Bowl and Dish description", mode="rule")
        )
        self.assertEqual(response.status, "ok")
        self.assertEqual(response.intent, "artifact_description")

    def test_artifact_dimensions(self) -> None:
        response = self.pipeline.handle_question(
            QAAskRequest(question="Tea Bowl and Dish dimensions?", mode="rule")
        )
        self.assertEqual(response.status, "ok")
        self.assertEqual(response.intent, "artifact_dimensions")

    def test_museum_count(self) -> None:
        response = self.pipeline.handle_question(
            QAAskRequest(question="Metropolitan Museum count?", mode="rule")
        )
        self.assertEqual(response.status, "ok")
        self.assertEqual(response.intent, "museum_count")

    def test_recommended_artifacts(self) -> None:
        response = self.pipeline.handle_question(
            QAAskRequest(question="Tea Bowl and Dish related?", mode="rule")
        )
        self.assertEqual(response.status, "ok")
        self.assertEqual(response.intent, "recommended_artifacts")

    def test_query_summary(self) -> None:
        self.pipeline.handle_question(QAAskRequest(question="Admonitions Scroll museum?", mode="rule"))
        self.pipeline.handle_question(QAAskRequest(question="Zhang Zeduan biography?", mode="rule"))
        self.pipeline.handle_question(QAAskRequest(question="blah blah?", mode="rule"))

        response = self.pipeline.summarize_queries()
        self.assertEqual(response.status, "ok")
        self.assertEqual(response.summary["total_questions"], 3)
        self.assertEqual(response.summary["intent_distribution"]["artifact_museum"], 1)
        self.assertEqual(response.summary["intent_distribution"]["artist_biography"], 1)
        self.assertEqual(response.summary["intent_distribution"]["unknown"], 1)
        self.assertEqual(response.summary["status_distribution"]["ok"], 2)
        self.assertEqual(response.summary["status_distribution"]["clarify"], 1)
        self.assertEqual(len(response.summary["failed_questions"]), 1)


if __name__ == "__main__":
    unittest.main()
