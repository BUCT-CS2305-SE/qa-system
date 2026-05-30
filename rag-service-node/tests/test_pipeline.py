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

    def test_ask_question_type_success(self) -> None:
        response = self.pipeline.handle_question(
            QAAskRequest(question="Tea Bowl and Dish是什么类型？", mode="rule")
        )
        self.assertEqual(response.status, "ok")
        self.assertEqual(response.intent, "artifact_type")
        self.assertIn("类型", response.answer)

    def test_ask_question_material_success(self) -> None:
        response = self.pipeline.handle_question(
            QAAskRequest(question="Tea Bowl and Dish是什么材质？", mode="rule")
        )
        self.assertEqual(response.status, "ok")
        self.assertEqual(response.intent, "artifact_material")
        self.assertIn("材质", response.answer)

    def test_ask_question_description_success(self) -> None:
        response = self.pipeline.handle_question(
            QAAskRequest(question="Tea Bowl and Dish请介绍", mode="rule")
        )
        self.assertEqual(response.status, "ok")
        self.assertEqual(response.intent, "artifact_description")
        self.assertIn("Tea Bowl and Dish", response.answer)

    def test_ask_question_dimensions_success(self) -> None:
        response = self.pipeline.handle_question(
            QAAskRequest(question="Tea Bowl and Dish的尺寸是多少？", mode="rule")
        )
        self.assertEqual(response.status, "ok")
        self.assertEqual(response.intent, "artifact_dimensions")
        self.assertIn("尺寸", response.answer)

    def test_museum_count_success(self) -> None:
        response = self.pipeline.handle_question(
            QAAskRequest(question="Art Institute of Chicago收藏了多少件中国文物？", mode="rule")
        )
        self.assertEqual(response.status, "ok")
        self.assertEqual(response.intent, "museum_count")
        self.assertIn("40", response.answer)

    def test_recommended_artifacts_success(self) -> None:
        response = self.pipeline.handle_question(
            QAAskRequest(question="Tea Bowl and Dish还有哪些文物推荐？", mode="rule")
        )
        self.assertEqual(response.status, "ok")
        self.assertEqual(response.intent, "recommended_artifacts")
        self.assertTrue(response.facts)
        self.assertIn("Tea Bowl and Dish", response.answer)

    def test_query_summary_includes_intent_and_failures(self) -> None:
        self.pipeline.handle_question(QAAskRequest(question="女史箴图现藏于哪家博物馆？", mode="rule"))
        self.pipeline.handle_question(QAAskRequest(question="顾恺之的生平经历是怎样的？", mode="rule"))
        self.pipeline.handle_question(QAAskRequest(question="这个东西好看吗？", mode="rule"))

        response = self.pipeline.summarize_queries()
        self.assertEqual(response.status, "ok")
        self.assertEqual(response.summary["total_questions"], 3)
        self.assertEqual(response.summary["intent_distribution"]["artifact_museum"], 1)
        self.assertEqual(response.summary["intent_distribution"]["artist_biography"], 1)
        self.assertEqual(response.summary["intent_distribution"]["unknown"], 1)
        self.assertEqual(response.summary["status_distribution"]["ok"], 1)
        self.assertEqual(response.summary["status_distribution"]["no_data"], 1)
        self.assertEqual(response.summary["status_distribution"]["clarify"], 1)
        self.assertEqual(len(response.summary["failed_questions"]), 2)


if __name__ == "__main__":
    unittest.main()