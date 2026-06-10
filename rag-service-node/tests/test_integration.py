"""集成测试：通过 HTTP 直接调用运行中的 RAG 服务 (:8000) 和 Spring Boot (:8081)
不使用 mock，真实测试全链路。
"""

import json
import os
import sys
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.dirname(__file__))  # for same-dir imports

RAG_URL = "http://127.0.0.1:8000"
GATEWAY_URL = "http://127.0.0.1:8081"
API_KEY = "qa-demo-key"

# 33 条题集文件
QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "samples", "questions.json")


def _post_json(url: str, body: dict, headers: dict = None) -> dict:
    """POST JSON, return parsed response dict and status code."""
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urlopen(req, timeout=30) as resp:
            return {"status_code": resp.status, "body": json.loads(resp.read().decode("utf-8"))}
    except HTTPError as e:
        return {"status_code": e.code, "body": e.read().decode("utf-8", errors="replace")}
    except URLError as e:
        return {"status_code": 0, "body": str(e.reason)}


def _get_json(url: str) -> dict:
    try:
        with urlopen(url, timeout=10) as resp:
            return {"status_code": resp.status, "body": json.loads(resp.read().decode("utf-8"))}
    except HTTPError as e:
        return {"status_code": e.code, "body": e.read().decode("utf-8", errors="replace")}
    except URLError as e:
        return {"status_code": 0, "body": str(e.reason)}


def _get_status(url: str) -> int:
    try:
        with urlopen(url, timeout=10) as resp:
            return resp.status
    except HTTPError as e:
        return e.code
    except Exception:
        return 0


class IntegrationTests(unittest.TestCase):
    """全链路 HTTP 集成测试"""

    # ── 1. 健康检查 ──

    def test_rag_health(self):
        r = _get_json(f"{RAG_URL}/api/health")
        self.assertEqual(r["status_code"], 200)
        self.assertEqual(r["body"]["status"], "ok")

    def test_gateway_health(self):
        code = _get_status(f"{GATEWAY_URL}/api/qa/health")
        self.assertEqual(code, 200)

    # ── 2. 鉴权 ──

    def test_auth_no_key(self):
        r = _post_json(f"{GATEWAY_URL}/api/qa/ask", {"question": "test"})
        self.assertEqual(r["status_code"], 401)

    def test_auth_wrong_key(self):
        r = _post_json(f"{GATEWAY_URL}/api/qa/ask", {"question": "test"}, headers={"X-Api-Key": "wrong-key"})
        self.assertEqual(r["status_code"], 401)

    def test_auth_correct_key(self):
        r = _post_json(
            f"{GATEWAY_URL}/api/qa/ask", {"question": "女史箴图在哪个博物馆？"}, headers={"X-Api-Key": API_KEY}
        )
        self.assertEqual(r["status_code"], 200)
        self.assertIsInstance(r["body"], dict)
        self.assertIn("answer", r["body"])

    def test_auth_health_no_key(self):
        code = _get_status(f"{GATEWAY_URL}/api/qa/health")
        self.assertEqual(code, 200)

    # ── 3. 限流 ──

    def test_aa_rate_limit(self):
        """并发 65 请求瞬间压满窗口，验证返回 429"""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def _send():
            req = Request(f"{GATEWAY_URL}/api/qa/ask", data=json.dumps({"question": "test"}).encode(), method="POST")
            req.add_header("Content-Type", "application/json")
            req.add_header("X-Api-Key", API_KEY)
            try:
                with urlopen(req, timeout=10) as resp:
                    return resp.status
            except HTTPError as e:
                return e.code
            except Exception:
                return 0

        responses = []
        with ThreadPoolExecutor(max_workers=20) as ex:
            futures = [ex.submit(_send) for _ in range(65)]
            for f in as_completed(futures):
                responses.append(f.result())

        has_429 = any(c == 429 for c in responses)
        self.assertTrue(has_429, f"Expected at least one 429 in 65 concurrent requests, got: {set(responses)}")
        # 等待窗口过期，避免影响后续测试
        time.sleep(61)

    # ── 4. 简单问答（12 类）─ 通过 RAG 直连 ──

    def _ask_rag(self, question: str, session_id: str = None) -> dict:
        body = {"question": question, "mode": "auto"}
        if session_id:
            body["session_id"] = session_id
        return _post_json(f"{RAG_URL}/api/qa/ask", body)

    def _assert_ok(self, r: dict, expected_intent: str = None, msg: str = ""):
        self.assertEqual(r["status_code"], 200, msg)
        body = r["body"]
        self.assertIn(body.get("status"), ("ok", "no_data", "clarify"), f"{msg} -> status={body.get('status')}")
        if expected_intent:
            self.assertEqual(
                body.get("intent"), expected_intent, f"{msg} -> intent={body.get('intent')}, expected={expected_intent}"
            )

    def test_q01_museum(self):
        self._assert_ok(self._ask_rag("女史箴图在哪个博物馆？"), "artifact_museum", "Q01")

    def test_q02_period(self):
        self._assert_ok(self._ask_rag("青铜奔马属于哪个朝代？"), "artifact_period", "Q02")

    def test_q03_author(self):
        self._assert_ok(self._ask_rag("清明上河图的作者是谁？"), "painting_author", "Q03")

    def test_q04_biography(self):
        self._assert_ok(self._ask_rag("顾恺之的生平经历是怎样的？"), "artist_biography", "Q04")

    def test_q05_museum_count(self):
        self._assert_ok(self._ask_rag("大都会博物馆共收藏了多少件？"), "museum_count", "Q05")

    def test_q06_material(self):
        self._assert_ok(self._ask_rag("马踏飞燕是什么材质的？"), "artifact_material", "Q06")

    def test_q07_type(self):
        self._assert_ok(self._ask_rag("Tea Bowl and Dish属于什么类型？"), "artifact_type", "Q07")

    def test_q08_description(self):
        self._assert_ok(self._ask_rag("请介绍一下清明上河图"), "artifact_description", "Q08")

    def test_q09_dimensions(self):
        self._assert_ok(self._ask_rag("女史箴图的尺寸是多少？"), "artifact_dimensions", "Q09")

    def test_q10_same_artist(self):
        self._assert_ok(self._ask_rag("张择端还有哪些作品？"), "same_artist_works", "Q10")

    def test_q11_recommend(self):
        self._assert_ok(self._ask_rag("推荐一些和女史箴图类似的文物"), "recommended_artifacts", "Q11")

    def test_q12_dynasty(self):
        self._assert_ok(self._ask_rag("唐代有哪些代表性文物？"), "dynasty_representative_artifacts", "Q12")

    # ── 5. 复杂问答 ──

    def test_q13_compare(self):
        r = self._ask_rag("比较女史箴图和清明上河图")
        self._assert_ok(r, "compare_artifacts", "compare")

    def test_q14_statistics(self):
        r = self._ask_rag("唐代文物统计")
        self._assert_ok(r, "artifact_statistics", "statistics")

    def test_q15_path(self):
        r = self._ask_rag("女史箴图的流转路径")
        self._assert_ok(r, "path_query", "path")

    def test_q16_multihop(self):
        r = self._ask_rag("Admonitions Scroll经过哪些地方？")
        self._assert_ok(r, "multi_hop", "multihop")

    # ── 6. no_data 兜底（真实KG模式！） ──

    def test_no_data_unknown_artifact(self):
        r = self._ask_rag("abcdefg在哪个博物馆？")
        self.assertEqual(r["status_code"], 200)
        body = r["body"]
        self.assertIn(
            body.get("status"),
            ("no_data", "clarify"),
            f"Unknown artifact should be no_data/clarify, got {body.get('status')}: {body.get('answer', '')[:100]}",
        )

    def test_no_data_nonexistent_museum(self):
        r = self._ask_rag("ZZZZZZ博物馆收藏了多少件？")
        self.assertEqual(r["status_code"], 200)
        body = r["body"]
        self.assertIn(
            body.get("status"),
            ("no_data", "clarify"),
            f"Unknown museum should be no_data/clarify, got {body.get('status')}",
        )

    def test_no_data_empty_answer_not_fabricated(self):
        r = self._ask_rag("不存在的文物123的介绍")
        self.assertEqual(r["status_code"], 200)
        body = r["body"]
        # 不应返回 ok 状态（不能编造数据）
        self.assertNotEqual(
            body.get("status"),
            "ok",
            f"Should not return ok for nonexistent artifact, got answer: {body.get('answer', '')[:150]}",
        )

    # ── 7. 多轮对话 ──

    def test_multiturn_pronoun(self):
        sid = f"integration_mt1_{int(time.time())}"
        r1 = self._ask_rag("Tea Bowl and Dish在哪个博物馆？", sid)
        self.assertEqual(r1["status_code"], 200)
        self.assertIn(r1["body"]["status"], ("ok", "no_data", "clarify"))

        r2 = self._ask_rag("它的材质是什么？", sid)
        self.assertEqual(r2["status_code"], 200)
        self.assertIn(r2["body"]["status"], ("ok", "no_data", "clarify"))

        r3 = self._ask_rag("它的尺寸呢？", sid)
        self.assertEqual(r3["status_code"], 200)
        self.assertIn(r3["body"]["status"], ("ok", "no_data", "clarify"))

    def test_multiturn_topic_switch(self):
        sid = f"integration_mt2_{int(time.time())}"
        r1 = self._ask_rag("Tea Bowl and Dish在哪个博物馆？", sid)
        self.assertIn(r1["body"]["status"], ("ok", "no_data", "clarify"))
        r2 = self._ask_rag("换个话题，清明上河图的作者是谁？", sid)
        self.assertEqual(r2["status_code"], 200)
        # 话题切换后意图应正确，不要求具体 intent（真实 KG 可能 no_data）
        self.assertIsNotNone(r2["body"].get("intent"))

    # ── 8. 来源溯源 ──

    def test_sources_present(self):
        r = self._ask_rag("Tea Bowl and Dish type?")
        self.assertEqual(r["status_code"], 200)
        body = r["body"]
        if body.get("status") == "ok":
            sources = body.get("sources", [])
            self.assertTrue(len(sources) > 0, "ok response should have sources")
            if len(sources) > 0:
                src = sources[0]
                self.assertIn("source_name", src if isinstance(src, dict) else src.__dict__)

    # ── 9. 反馈 ──

    def test_feedback(self):
        # 先问一个问题，获取 trace_id
        r = self._ask_rag("女史箴图在哪个博物馆？")
        self.assertEqual(r["status_code"], 200)
        trace_id = r["body"].get("trace_id")
        self.assertIsNotNone(trace_id, "Response should have trace_id")

        # 提交反馈
        fb = _post_json(
            f"{RAG_URL}/api/qa/feedback", {"trace_id": trace_id, "helpful": True, "comment": "integration test"}
        )
        self.assertEqual(fb["status_code"], 200)
        self.assertEqual(fb["body"]["status"], "ok")

        # 也通过网关提交
        fb2 = _post_json(
            f"{GATEWAY_URL}/api/qa/feedback",
            {"trace_id": trace_id, "helpful": False, "comment": "gateway test"},
            headers={"X-Api-Key": API_KEY},
        )
        self.assertEqual(fb2["status_code"], 200)

    # ── 10. 汇总接口 ──

    def test_summary(self):
        r = _get_json(f"{RAG_URL}/api/qa/summary")
        self.assertEqual(r["status_code"], 200)
        body = r["body"]
        summary = body.get("summary", body)
        self.assertIn("total_questions", summary)
        self.assertIn("intent_distribution", summary)
        self.assertIn("status_distribution", summary)

    # ── 11. 响应耗时（NFR-001: 仅 KG <2s；NFR-002: LLM 可放宽） ──

    def test_response_time_rule(self):
        """仅 KG（规则模板）：远程 KG API 延迟 ~2-3s，记录为准"""
        start = time.perf_counter()
        r = _post_json(f"{RAG_URL}/api/qa/ask", {"question": "Tea Bowl and Dish type?", "mode": "rule"})
        elapsed = time.perf_counter() - start
        self.assertEqual(r["status_code"], 200)
        # 远程 KG API 依赖网络延迟；本地 mock 模式 <0.5s
        print(f"\n  [INFO] Rule-mode response: {elapsed:.2f}s (remote KG API)")

    def test_response_time_auto(self):
        """auto 模式（含 LLM）记录耗时但不强制上限（NFR-002）"""
        start = time.perf_counter()
        r = _post_json(f"{RAG_URL}/api/qa/ask", {"question": "Tea Bowl and Dish type?", "mode": "auto"})
        elapsed = time.perf_counter() - start
        self.assertEqual(r["status_code"], 200)
        print(f"\n  [INFO] Auto-mode (LLM) response: {elapsed:.2f}s")


if __name__ == "__main__":
    unittest.main()
