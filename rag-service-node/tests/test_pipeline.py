import unittest
from app.api.routes.health import health_check
from app.models.api import FeedbackRequest, QAAskRequest
from app.orchestration.qa_pipeline import QAPipeline

class PipelineTests(unittest.TestCase):
    def setUp(self): self.pipeline = QAPipeline()
    def test_health(self):
        self.assertEqual(health_check()["status"], "ok")
    def test_artifact_museum(self):
        r = self.pipeline.handle_question(QAAskRequest(question="Admonitions Scroll museum?", mode="rule"))
        self.assertEqual(r.status, "ok"); self.assertEqual(r.intent, "artifact_museum")
    def test_artist_biography_success(self):
        r = self.pipeline.handle_question(QAAskRequest(question="Zhang Zeduan biography?", mode="rule"))
        self.assertEqual(r.status, "ok"); self.assertEqual(r.intent, "artist_biography")
    def test_same_artist_works(self):
        r = self.pipeline.handle_question(QAAskRequest(question="Zhang Zeduan other works?", mode="rule"))
        self.assertEqual(r.status, "ok"); self.assertEqual(r.intent, "same_artist_works"); self.assertIn("Zhang Zeduan", r.answer)
    def test_unknown_question_clarify(self):
        r = self.pipeline.handle_question(QAAskRequest(question="blah blah?", mode="rule"))
        self.assertEqual(r.status, "clarify")
    def test_feedback(self):
        r = self.pipeline.record_feedback(FeedbackRequest(trace_id="t1", helpful=True, comment="u"))
        self.assertEqual(r.status, "ok")
    def test_artifact_type(self):
        r = self.pipeline.handle_question(QAAskRequest(question="Tea Bowl and Dish type?", mode="rule"))
        self.assertEqual(r.status, "ok"); self.assertEqual(r.intent, "artifact_type")
    def test_artifact_material(self):
        r = self.pipeline.handle_question(QAAskRequest(question="Bronze Galloping Horse material?", mode="rule"))
        self.assertEqual(r.status, "ok"); self.assertEqual(r.intent, "artifact_material")
    def test_artifact_description(self):
        r = self.pipeline.handle_question(QAAskRequest(question="Tea Bowl and Dish description", mode="rule"))
        self.assertEqual(r.status, "ok"); self.assertEqual(r.intent, "artifact_description")
    def test_artifact_dimensions(self):
        r = self.pipeline.handle_question(QAAskRequest(question="Tea Bowl and Dish dimensions?", mode="rule"))
        self.assertEqual(r.status, "ok"); self.assertEqual(r.intent, "artifact_dimensions")
    def test_museum_count(self):
        r = self.pipeline.handle_question(QAAskRequest(question="Metropolitan Museum count?", mode="rule"))
        self.assertEqual(r.status, "ok"); self.assertEqual(r.intent, "museum_count")
    def test_recommended_artifacts(self):
        r = self.pipeline.handle_question(QAAskRequest(question="Tea Bowl and Dish related?", mode="rule"))
        self.assertEqual(r.status, "ok"); self.assertEqual(r.intent, "recommended_artifacts")
    def test_query_summary(self):
        self.pipeline.handle_question(QAAskRequest(question="Admonitions Scroll museum?", mode="rule"))
        self.pipeline.handle_question(QAAskRequest(question="Zhang Zeduan biography?", mode="rule"))
        self.pipeline.handle_question(QAAskRequest(question="blah blah?", mode="rule"))
        r = self.pipeline.summarize_queries()
        self.assertEqual(r.status, "ok"); self.assertEqual(r.summary["total_questions"], 3)
        self.assertEqual(r.summary["intent_distribution"]["artifact_museum"], 1)
        self.assertEqual(r.summary["intent_distribution"]["artist_biography"], 1)
        self.assertEqual(r.summary["intent_distribution"]["unknown"], 1)
        self.assertEqual(r.summary["status_distribution"]["ok"], 2)
        self.assertEqual(r.summary["status_distribution"]["clarify"], 1)
        self.assertEqual(len(r.summary["failed_questions"]), 1)

if __name__ == "__main__": unittest.main()
