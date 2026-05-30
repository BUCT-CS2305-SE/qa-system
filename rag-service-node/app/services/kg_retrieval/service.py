from __future__ import annotations

import json
import urllib.parse
import urllib.request
from html import unescape

from app.core.config import settings
from app.models.domain import RetrievalResult, RetrievedFact
from app.services.kg_retrieval.mock_data import MOCK_RESULTS


class KGRetrievalService:
    def retrieve(self, template_name: str | None, query_text: str | None, parameters: dict[str, object]) -> RetrievalResult:
        if not template_name or not query_text:
            return RetrievalResult(status="no_data", fail_reason="未生成查询语句")

        if settings.graph_backend in {"remote", "hybrid"}:
            remote_result = self._retrieve_from_remote(template_name, parameters)
            if remote_result is not None:
                return remote_result

        return self._retrieve_from_mock(template_name)

    def _retrieve_from_remote(self, template_name: str, parameters: dict[str, object]) -> RetrievalResult | None:
        try:
            if template_name in {
                "artifact_museum_query",
                "artifact_period_query",
                "artifact_material_query",
                "artifact_type_query",
                "artifact_description_query",
                "artifact_dimensions_query",
            }:
                artifact_name = str(parameters.get("artifact_name", "")).strip()
                if not artifact_name:
                    return RetrievalResult(status="no_data", fail_reason="缺少文物名称")
                object_id = self._resolve_object_id(artifact_name)
                if not object_id:
                    return None if settings.graph_backend == "hybrid" else RetrievalResult(status="no_data", fail_reason="知识图谱未命中文物")

                prop_map = {
                    "artifact_museum_query": "museum",
                    "artifact_period_query": "period",
                    "artifact_material_query": "material",
                    "artifact_type_query": "type",
                    "artifact_description_query": "description",
                }
                detail_payload = self._get_json(f"/api/artifacts/{object_id}")
                if template_name == "artifact_dimensions_query":
                    return self._build_detail_result(template_name, artifact_name, object_id, detail_payload)

                prop = prop_map[template_name]
                property_payload = self._get_json(f"/api/artifacts/{object_id}/property?prop={prop}")
                return self._build_property_result(template_name, artifact_name, object_id, property_payload, detail_payload)

            if template_name == "recommended_artifacts_query":
                artifact_name = str(parameters.get("artifact_name", "")).strip()
                if not artifact_name:
                    return RetrievalResult(status="no_data", fail_reason="缺少文物名称")
                object_id = self._resolve_object_id(artifact_name)
                if not object_id:
                    return None if settings.graph_backend == "hybrid" else RetrievalResult(status="no_data", fail_reason="知识图谱未命中文物")

                detail_payload = self._get_json(f"/api/artifacts/{object_id}")
                return self._build_recommendation_result(artifact_name, object_id, detail_payload)

            if template_name == "museum_count_query":
                stats_payload = self._get_json("/api/stats/summary")
                museum_name = str(parameters.get("museum_name", "")).strip()
                return self._build_stats_result(museum_name, stats_payload)
        except Exception as error:
            if settings.graph_backend == "remote":
                return RetrievalResult(status="no_data", fail_reason=f"知识图谱接口调用失败: {error}")
        return None

    def _retrieve_from_mock(self, template_name: str) -> RetrievalResult:

        records = MOCK_RESULTS.get(template_name, [])
        facts = []
        for record in records:
            for key, value in record.items():
                if key not in {"source_name", "source_url"}:
                    facts.append(
                        RetrievedFact(
                            subject=record.get("artifact") or record.get("artist") or record.get("museum") or "result",
                            predicate=key,
                            object=str(value),
                            source_name=record.get("source_name"),
                            source_url=record.get("source_url"),
                        )
                    )
        status = "ok" if records else "no_data"
        return RetrievalResult(status=status, facts=facts, raw_records=records, fail_reason=None if records else "暂无相关数据")

    def _resolve_object_id(self, artifact_name: str) -> str | None:
        payload = self._get_json(f"/api/search?q={urllib.parse.quote(artifact_name)}&page=1&page_size=10")
        candidates = payload.get("data", []) if isinstance(payload, dict) else []
        if not candidates:
            return None

        normalized_target = self._normalize_text(artifact_name)
        exact_match = next(
            (
                item for item in candidates
                if self._normalize_text(str(item.get("name", ""))) == normalized_target
            ),
            None,
        )
        selected = exact_match or candidates[0]
        object_id = selected.get("id")
        return str(object_id) if object_id is not None else None

    def _build_property_result(
        self,
        template_name: str,
        artifact_name: str,
        object_id: str,
        property_payload: dict[str, object],
        detail_payload: dict[str, object],
    ) -> RetrievalResult:
        prop = str(property_payload.get("prop", ""))
        value = property_payload.get("value")
        source_name = str(detail_payload.get("museum", "")) or None
        source_url = str(detail_payload.get("detail_url", "")) or None
        artifact = str(detail_payload.get("name", artifact_name))

        if value in (None, ""):
            return RetrievalResult(status="no_data", fail_reason="知识图谱属性为空")

        object_key_map = {
            "artifact_museum_query": "museum",
            "artifact_period_query": "dynasty",
            "artifact_material_query": "material",
            "artifact_type_query": "type",
            "artifact_description_query": "description",
        }
        object_key = object_key_map[template_name]
        raw_record = {
            "id": object_id,
            "artifact": artifact,
            object_key: str(value),
            "source_name": source_name,
            "source_url": source_url,
        }
        facts = [
            RetrievedFact(
                subject=artifact,
                predicate="artifact",
                object=artifact,
                source_name=source_name,
                source_url=source_url,
            ),
            RetrievedFact(
                subject=artifact,
                predicate=prop,
                object=str(value),
                source_name=source_name,
                source_url=source_url,
            ),
        ]
        return RetrievalResult(status="ok", facts=facts, raw_records=[raw_record])

    def _build_detail_result(
        self,
        template_name: str,
        artifact_name: str,
        object_id: str,
        detail_payload: dict[str, object],
    ) -> RetrievalResult:
        artifact = str(detail_payload.get("name", artifact_name))
        source_name = str(detail_payload.get("museum", "")) or None
        source_url = str(detail_payload.get("detail_url", "")) or None

        field_map = {
            "artifact_dimensions_query": "dimensions",
        }
        field_name = field_map[template_name]
        value = detail_payload.get(field_name)
        if value in (None, ""):
            return RetrievalResult(status="no_data", fail_reason="知识图谱详情字段为空")

        raw_record = {
            "id": object_id,
            "artifact": artifact,
            field_name: str(value),
            "source_name": source_name,
            "source_url": source_url,
        }
        facts = [
            RetrievedFact(
                subject=artifact,
                predicate="artifact",
                object=artifact,
                source_name=source_name,
                source_url=source_url,
            ),
            RetrievedFact(
                subject=artifact,
                predicate=field_name,
                object=str(value),
                source_name=source_name,
                source_url=source_url,
            ),
        ]
        return RetrievalResult(status="ok", facts=facts, raw_records=[raw_record])

    def _build_stats_result(self, museum_name: str, stats_payload: dict[str, object]) -> RetrievalResult:
        top_museums = stats_payload.get("top_museums", []) if isinstance(stats_payload, dict) else []
        matched = next(
            (
                item for item in top_museums
                if self._normalize_text(str(item.get("name", ""))) == self._normalize_text(museum_name)
            ),
            None,
        )
        if not matched:
            return RetrievalResult(status="no_data", fail_reason="知识图谱统计中未命中该博物馆")

        museum = str(matched.get("name", museum_name))
        count = matched.get("count", 0)
        raw_record = {
            "museum": museum,
            "artifact_count": int(count),
            "source_name": "中国海外流失文物知识图谱 API",
            "source_url": f"{settings.kg_api_base_url}/docs",
        }
        facts = [
            RetrievedFact(
                subject=museum,
                predicate="artifact_count",
                object=str(count),
                source_name="中国海外流失文物知识图谱 API",
                source_url=f"{settings.kg_api_base_url}/docs",
            )
        ]
        return RetrievalResult(status="ok", facts=facts, raw_records=[raw_record])

    def _build_recommendation_result(
        self,
        artifact_name: str,
        object_id: str,
        detail_payload: dict[str, object],
    ) -> RetrievalResult:
        artifact = str(detail_payload.get("name", artifact_name))
        museum_name = str(detail_payload.get("museum", "")).strip()
        period_name = str(detail_payload.get("period", "")).strip()
        type_name = str(detail_payload.get("type", "")).strip()
        source_url = str(detail_payload.get("detail_url", "")) or None

        candidate_ids: list[str] = []
        for query in [museum_name, period_name, type_name]:
            if not query:
                continue
            payload = self._get_json(f"/api/search?q={urllib.parse.quote(query)}&page=1&page_size=8")
            for item in payload.get("data", []) if isinstance(payload, dict) else []:
                candidate_id = item.get("id")
                if candidate_id is None:
                    continue
                candidate_id_str = str(candidate_id)
                if candidate_id_str not in candidate_ids and candidate_id_str != object_id:
                    candidate_ids.append(candidate_id_str)

        scored_candidates: list[tuple[int, dict[str, object]]] = []
        for candidate_id in candidate_ids[:8]:
            candidate_detail = self._get_json(f"/api/artifacts/{candidate_id}")
            score = 0
            if self._normalize_text(str(candidate_detail.get("museum", ""))) == self._normalize_text(museum_name):
                score += 2
            if self._normalize_text(str(candidate_detail.get("type", ""))) == self._normalize_text(type_name):
                score += 2
            if self._normalize_text(str(candidate_detail.get("period", ""))) == self._normalize_text(period_name):
                score += 1
            scored_candidates.append((score, candidate_detail))

        scored_candidates.sort(
            key=lambda item: (
                item[0],
                self._normalize_text(str(item[1].get("name", ""))),
            ),
            reverse=True,
        )
        selected_candidates = [detail for score, detail in scored_candidates if score > 0][:3]
        if not selected_candidates:
            return RetrievalResult(status="no_data", fail_reason="未找到可推荐的相关文物")

        recommendation_names = [str(item.get("name", "")) for item in selected_candidates if item.get("name")]
        raw_record = {
            "artifact": artifact,
            "recommendations": recommendation_names,
            "source_name": museum_name or "中国海外流失文物知识图谱 API",
            "source_url": source_url or f"{settings.kg_api_base_url}/docs",
        }
        facts = [
            RetrievedFact(
                subject=artifact,
                predicate="recommended_artifact",
                object=name,
                source_name=str(item.get("museum", museum_name)) or (museum_name or "中国海外流失文物知识图谱 API"),
                source_url=str(item.get("detail_url", "")) or (source_url or f"{settings.kg_api_base_url}/docs"),
            )
            for name, item in zip(recommendation_names, selected_candidates)
        ]
        return RetrievalResult(status="ok", facts=facts, raw_records=[raw_record])

    def _get_json(self, path: str) -> dict[str, object]:
        base_url = settings.kg_api_base_url.rstrip("/")
        request = urllib.request.Request(f"{base_url}{path}", method="GET")
        with urllib.request.urlopen(request, timeout=settings.kg_api_timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8", errors="replace"))

    def _normalize_text(self, value: str) -> str:
        return unescape(value).replace("�", "-").strip().lower()