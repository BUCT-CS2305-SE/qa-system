"""回归测试：使用 questions.json 33条题集跑全链路，输出通过率与失败原因。"""

import json
import os
import unittest

os.environ["qa_graph_backend"] = "mock"
os.environ["qa_llm_backend"] = "mock"

from app.models.api import QAAskRequest
from app.orchestration.qa_pipeline import QAPipeline

QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "samples", "questions.json")

# ── 题目 → 预期意图 映射 ──
EXPECTED_INTENT = {
    0: "artifact_museum",
    1: "artifact_period",
    2: "painting_author",
    3: "artist_biography",
    4: "museum_count",
    5: "artifact_material",
    6: "artifact_type",
    7: "artifact_description",
    8: "artifact_dimensions",
    9: "same_artist_works",
    10: "recommended_artifacts",
    11: "dynasty_representative_artifacts",
    12: "artifact_museum",
    13: "artifact_period",
    14: "artifact_material",
    15: "artifact_dimensions",
    16: "painting_author",
    17: "dynasty_representative_artifacts",
    18: "museum_count",
    19: "same_artist_works",
    20: "artifact_type",
    21: "artifact_description",
    22: "artist_biography",
    23: "museum_count",
    24: "artifact_museum",
    25: "artifact_period",
    26: "dynasty_representative_artifacts",
    27: "compare_artifacts",
    28: "artifact_statistics",
    29: "path_query",
    30: "multi_hop",
    # 31-32: 多轮对话，无独立意图映射（需上下文）
}


class RegressionTests(unittest.TestCase):
    """33条题集回归测试"""

    @classmethod
    def setUpClass(cls):
        cls.pipeline = QAPipeline()
        with open(QUESTIONS_FILE, encoding="utf-8") as f:
            cls.questions = json.load(f)
        cls.results = []
        cls.failures = []

    def _run_one(self, idx: int, question: str, session_id: str = None):
        """执行单条问题并记录结果"""
        try:
            r = self.pipeline.handle_question(QAAskRequest(question=question, session_id=session_id, mode="rule"))
            return r
        except Exception as e:
            return {"status": "error", "intent": None, "answer": "", "code": str(e), "no_data": False, "error": str(e)}

    # ── 第 1-31 条：独立问答 ──

    def _test_single(self, idx: int):
        q = self.questions[idx]
        session_id = f"regr_simple_{idx}"
        r = self._run_one(idx, q, session_id)

        self.results.append({"idx": idx + 1, "question": q, "status": r.status, "intent": r.intent})

        # 基础校验：不能是 error
        self.assertNotEqual(r.status, "error", f"#{idx + 1} '{q}' → status=error: {getattr(r, 'error', '')}")

        # 状态必须是 ok / no_data / clarify 之一
        self.assertIn(r.status, ("ok", "no_data", "clarify"), f"#{idx + 1} '{q}' → unexpected status={r.status}")

        # 如果有预期意图，校验意图匹配
        expected = EXPECTED_INTENT.get(idx)
        if expected is not None and r.status != "clarify":
            self.assertEqual(r.intent, expected, f"#{idx + 1} '{q}' → intent={r.intent}, expected={expected}")

    def test_01_artifact_museum(self):
        self._test_single(0)

    def test_02_artifact_period(self):
        self._test_single(1)

    def test_03_painting_author(self):
        self._test_single(2)

    def test_04_artist_biography(self):
        self._test_single(3)

    def test_05_museum_count(self):
        self._test_single(4)

    def test_06_artifact_material(self):
        self._test_single(5)

    def test_07_artifact_type(self):
        self._test_single(6)

    def test_08_artifact_description(self):
        self._test_single(7)

    def test_09_artifact_dimensions(self):
        self._test_single(8)

    def test_10_same_artist_works(self):
        self._test_single(9)

    def test_11_recommended_artifacts(self):
        self._test_single(10)

    def test_12_dynasty_representative(self):
        self._test_single(11)

    def test_13_artifact_museum_en(self):
        self._test_single(12)

    def test_14_artifact_period2(self):
        self._test_single(13)

    def test_15_artifact_material2(self):
        self._test_single(14)

    def test_16_artifact_dimensions2(self):
        self._test_single(15)

    def test_17_painting_author2(self):
        self._test_single(16)

    def test_18_dynasty_representative2(self):
        self._test_single(17)

    def test_19_museum_count2(self):
        self._test_single(18)

    def test_20_same_artist_works2(self):
        self._test_single(19)

    def test_21_artifact_type2(self):
        self._test_single(20)

    def test_22_artifact_description2(self):
        self._test_single(21)

    def test_23_artist_biography2(self):
        self._test_single(22)

    def test_24_museum_count3(self):
        self._test_single(23)

    def test_25_artifact_museum_qmsht(self):
        self._test_single(24)

    def test_26_artifact_period_nszht(self):
        self._test_single(25)

    def test_27_dynasty_tang(self):
        self._test_single(26)

    def test_28_compare_artifacts(self):
        self._test_single(27)

    def test_29_artifact_statistics(self):
        self._test_single(28)

    def test_30_path_query(self):
        self._test_single(29)

    def test_31_multi_hop(self):
        self._test_single(30)

    # ── 第 32-33 条：多轮对话 ──

    def test_32_pronoun_resolution(self):
        """#32 '它的材质是什么？' — 需要前序上下文"""
        sid = "regr_multi_1"
        # 先发一条建立上下文
        r1 = self._run_one(0, "女史箴图在哪个博物馆？", sid)
        self.assertEqual(r1.status, "ok")
        # 再发代词问题
        q = self.questions[31]
        r2 = self._run_one(31, q, sid)
        self.results.append({"idx": 32, "question": q, "status": r2.status, "intent": r2.intent})
        self.assertIn(r2.status, ("ok", "no_data", "clarify"), f"#32 pronoun '{q}' → status={r2.status}")

    def test_33_topic_switch(self):
        """#33 '换一个话题，清明上河图的作者是谁？' — 话题切换"""
        sid = "regr_multi_2"
        r1 = self._run_one(0, "女史箴图在哪个博物馆？", sid)
        self.assertEqual(r1.status, "ok")
        q = self.questions[32]
        r2 = self._run_one(32, q, sid)
        self.results.append({"idx": 33, "question": q, "status": r2.status, "intent": r2.intent})
        self.assertIn(r2.status, ("ok", "no_data", "clarify"), f"#33 topic switch '{q}' → status={r2.status}")
        self.assertEqual(r2.intent, "painting_author", f"#33 expected painting_author, got {r2.intent}")

    # ── no_data 兜底（mock 模式行为） ──
    # 注意：mock 模式下意图匹配成功即返回 mock 数据，no_data 行为需对接真实 KG API 验证

    def test_no_data_unknown_entity(self):
        """未知实体：mock 模式下不崩溃即可，真实 KG 模式应返回 no_data"""
        for q in ["一块不知名石头的材质是什么？", "abcdefg在哪个博物馆？", "不存在的文物123的介绍"]:
            r = self._run_one(99, q, "nd_test")
            self.results.append({"idx": "ND", "question": q, "status": r.status, "intent": r.intent})
            # mock 模式：已知意图会返回 mock 数据(status=ok)，不会报 error
            self.assertNotEqual(r.status, "error", f"'{q}' should not crash, got status={r.status}")

    def test_source_present_on_ok(self):
        """status=ok 的回答应包含 sources"""
        r = self._run_one(0, "女史箴图在哪个博物馆？", "src_test")
        self.assertEqual(r.status, "ok")
        self.assertIsNotNone(r.sources, "sources should not be None")
        self.assertTrue(len(r.sources) > 0, "sources should be non-empty for ok answer")
        src = r.sources[0]
        self.assertIn("source_name", src.__dict__ if hasattr(src, "__dict__") else src)

    def test_feedback_recording(self):
        """反馈记录不应报错"""
        from app.models.api import FeedbackRequest

        r = self.pipeline.record_feedback(FeedbackRequest(trace_id="regr_fb", helpful=True, comment="test"))
        self.assertEqual(r.status, "ok")


if __name__ == "__main__":
    unittest.main()
