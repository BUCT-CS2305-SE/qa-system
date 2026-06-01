from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from html import unescape

from app.core.config import settings
from app.models.domain import RetrievalResult, RetrievedFact
from app.services.kg_retrieval.mock_data import MOCK_RESULTS

logger = logging.getLogger(__name__)


class KGRetrievalService:

    # ── Public entry ────────────────────────────────────────────

    def retrieve(self, template_name: str | None, query_text: str | None, parameters: dict[str, object]) -> RetrievalResult:
        if not template_name or not query_text:
            return RetrievalResult(status="no_data", fail_reason="未生成查询语句")

        if settings.graph_backend in {"remote", "hybrid"}:
            remote_result = self._retrieve_from_remote(template_name, parameters)
            if remote_result is not None:
                logger.info("KG data source: remote (template=%s, status=%s)", template_name, remote_result.status)
                return remote_result

        logger.info("KG data source: mock (template=%s)", template_name)
        return self._retrieve_from_mock(template_name)

    # ── Remote dispatch ────────────────────────────────────────

    _ARTIFACT_DETAIL_INTENTS = {
        "artifact_museum_query",
        "artifact_period_query",
        "artifact_material_query",
        "artifact_type_query",
        "artifact_description_query",
        "artifact_dimensions_query",
        "painting_author_query",
    }

    def _retrieve_from_remote(self, template_name: str, parameters: dict[str, object]) -> RetrievalResult | None:
        try:
            if template_name in self._ARTIFACT_DETAIL_INTENTS:
                return self._resolve_and_query_artifact(template_name, parameters)

            if template_name == "recommended_artifacts_query":
                return self._query_related_artifacts(parameters)

            if template_name == "artist_biography_query":
                return self._query_artist_biography(parameters)

            if template_name == "dynasty_representative_query":
                return self._query_dynasty_representative(parameters)

            if template_name == "museum_count_query":
                return self._query_museum_count(parameters)

            if template_name == "same_artist_works_query":
                return self._query_same_artist_works(parameters)

            # ── Complex QA ────────────────────────────────────

            if template_name == "multi_hop_query":
                return self._query_multi_hop(parameters)

            if template_name == "compare_artifacts_query":
                return self._query_compare_artifacts(parameters)

            if template_name == "artifact_statistics_query":
                return self._query_artifact_statistics(parameters)

            if template_name == "path_query":
                return self._query_graph_path(parameters)

        except Exception as error:
            if settings.graph_backend == "remote":
                return RetrievalResult(status="no_data", fail_reason=f"知识图谱接口调用失败: {error}")
        return None

    # ── Artifact property queries (search → detail / property) ──

    _PROP_MAP = {
        "artifact_museum_query": "museum",
        "artifact_period_query": "period",
        "artifact_material_query": "material",
        "artifact_type_query": "type",
        "artifact_description_query": "description",
    }

    def _resolve_and_query_artifact(self, template_name: str, parameters: dict[str, object]) -> RetrievalResult | None:
        artifact_name = str(parameters.get("artifact_name", "")).strip()
        if not artifact_name:
            return RetrievalResult(status="no_data", fail_reason="缺少文物名称")

        object_id = self._resolve_object_id(artifact_name)
        if not object_id:
            return (
                None if settings.graph_backend == "hybrid"
                else RetrievalResult(status="no_data", fail_reason="知识图谱未命中文物")
            )

        if template_name == "artifact_dimensions_query":
            detail = self._get_json(f"/api/artifacts/{object_id}")
            return self._build_detail_result(template_name, artifact_name, object_id, detail)

        if template_name == "painting_author_query":
            detail = self._get_json(f"/api/artifacts/{object_id}")
            return self._build_author_result(artifact_name, object_id, detail)

        prop = self._PROP_MAP[template_name]
        detail = self._get_json(f"/api/artifacts/{object_id}")
        property_payload = self._get_json(f"/api/artifacts/{object_id}/property?prop={prop}")
        return self._build_property_result(template_name, artifact_name, object_id, property_payload, detail)

    # ── Related artifacts (data team's /api/artifacts/{id}/related) ──

    def _query_related_artifacts(self, parameters: dict[str, object]) -> RetrievalResult | None:
        artifact_name = str(parameters.get("artifact_name", "")).strip()
        if not artifact_name:
            return RetrievalResult(status="no_data", fail_reason="缺少文物名称")

        object_id = self._resolve_object_id(artifact_name)
        if not object_id:
            return (
                None if settings.graph_backend == "hybrid"
                else RetrievalResult(status="no_data", fail_reason="知识图谱未命中文物")
            )

        detail = self._get_json(f"/api/artifacts/{object_id}")
        artifact = str(detail.get("name", artifact_name))
        museum_name = str(detail.get("museum", ""))
        source_url = str(detail.get("detail_url", "")) or None

        # Use data team's related endpoint
        related_payload = self._get_json(f"/api/artifacts/{object_id}/related?top_k=3&lang=zh")
        related_items = related_payload.get("data", []) if isinstance(related_payload, dict) else []

        recommendation_names = [str(item.get("name", "")) for item in related_items if item.get("name")]
        if not recommendation_names:
            return (
                None if settings.graph_backend == "hybrid"
                else RetrievalResult(status="no_data", fail_reason="未找到可推荐的相关文物")
            )

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
                source_name=str(item.get("museum", museum_name)) or (museum_name or source_url or ""),
                source_url=str(item.get("detail_url", "")) or source_url or "",
            )
            for name, item in zip(recommendation_names, related_items)
        ]
        return RetrievalResult(status="ok", facts=facts, raw_records=[raw_record])

    # ── Artist biography (via /api/qa/grounding/{id}) ──

    def _query_artist_biography(self, parameters: dict[str, object]) -> RetrievalResult | None:
        artist_name = str(parameters.get("artist_name", "")).strip()
        if not artist_name:
            return RetrievalResult(status="no_data", fail_reason="缺少作者名称")

        # Search for the artist's artifact to get an object_id for grounding
        # Fallback: the data team's /api/qa/grounding uses artifact IDs, not artist IDs.
        # We search for the artist name and use the first matching artifact's grounding context.
        search_payload = self._get_json(f"/api/search?q={urllib.parse.quote(artist_name)}&page=1&page_size=1&lang=zh")
        candidates = search_payload.get("data", []) if isinstance(search_payload, dict) else []
        if not candidates:
            return (
                None if settings.graph_backend == "hybrid"
                else RetrievalResult(status="no_data", fail_reason="未找到该作者相关信息")
            )
        object_id = str(candidates[0].get("id", ""))

        # Use grounding context for comprehensive facts
        grounding = self._get_json(f"/api/qa/grounding/{object_id}?lang=zh")
        artist_field = grounding.get("artist") or grounding.get("author") or ""
        biography = grounding.get("artist_biography") or grounding.get("artist_bio") or ""

        raw_record = {
            "artist": artist_name,
            "biography": biography or f"{artist_name}的相关信息",
            "source_name": str(grounding.get("source_name") or candidates[0].get("museum", "")),
            "source_url": str(grounding.get("source_url") or candidates[0].get("detail_url", "")),
        }
        facts = [
            RetrievedFact(
                subject=artist_name,
                predicate="biography",
                object=raw_record["biography"],
                source_name=raw_record["source_name"],
                source_url=raw_record["source_url"],
            )
        ]
        return RetrievalResult(status="ok", facts=facts, raw_records=[raw_record])

    # ── Dynasty representative artifacts (via /api/qa/query) ──

    def _query_dynasty_representative(self, parameters: dict[str, object]) -> RetrievalResult | None:
        dynasty_name = str(parameters.get("dynasty_name", "")).strip()
        if not dynasty_name:
            return RetrievalResult(status="no_data", fail_reason="缺少朝代名称")

        if settings.qa_query_enabled:
            payload = json.dumps({"intent": "artifacts_of_period", "params": {"period": dynasty_name}}).encode()
            req = urllib.request.Request(
                f"{settings.kg_api_base_url}/api/qa/query",
                data=payload, method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=settings.kg_api_timeout_seconds) as resp:
                data = json.loads(resp.read())
            items = data.get("data", []) if isinstance(data, dict) else []
            artifact_names = [str(item.get("name", "")) for item in items if item.get("name")]
        else:
            # Fallback: use search to find artifacts by period
            search_payload = self._get_json(f"/api/search?q={urllib.parse.quote(dynasty_name)}&page=1&page_size=10&lang=zh")
            items = search_payload.get("data", []) if isinstance(search_payload, dict) else []
            artifact_names = [str(item.get("name", "")) for item in items if item.get("name")]

        if not artifact_names:
            return (
                None if settings.graph_backend == "hybrid"
                else RetrievalResult(status="no_data", fail_reason="未找到该朝代相关文物")
            )

        raw_record = {
            "dynasty": dynasty_name,
            "artifacts": artifact_names,
            "source_name": "中国海外流失文物知识图谱 API",
            "source_url": f"{settings.kg_api_base_url}/docs",
        }
        facts = [
            RetrievedFact(
                subject=dynasty_name,
                predicate="representative_artifacts",
                object="、".join(artifact_names),
                source_name=raw_record["source_name"],
                source_url=raw_record["source_url"],
            )
        ]
        return RetrievalResult(status="ok", facts=facts, raw_records=[raw_record])

    # ── Museum count (via /api/stats/summary) ──

    def _query_museum_count(self, parameters: dict[str, object]) -> RetrievalResult | None:
        stats = self._get_json("/api/stats/summary")
        museum_name = str(parameters.get("museum_name", "")).strip()
        top_museums = stats.get("top_museums", []) if isinstance(stats, dict) else []
        matched = next(
            (item for item in top_museums
             if self._normalize_text(str(item.get("name", ""))) == self._normalize_text(museum_name)),
            None,
        )
        if not matched:
            return (
                None if settings.graph_backend == "hybrid"
                else RetrievalResult(status="no_data", fail_reason="知识图谱统计中未命中该博物馆")
            )

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
                source_name=raw_record["source_name"],
                source_url=raw_record["source_url"],
            )
        ]
        return RetrievalResult(status="ok", facts=facts, raw_records=[raw_record])

    # ── Build helpers ──────────────────────────────────────────

    def _build_property_result(self, template_name: str, artifact_name: str, object_id: str,
                               property_payload: dict, detail_payload: dict) -> RetrievalResult:
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
            RetrievedFact(subject=artifact, predicate=prop, object=str(value),
                          source_name=source_name, source_url=source_url),
        ]
        return RetrievalResult(status="ok", facts=facts, raw_records=[raw_record])

    def _build_detail_result(self, template_name: str, artifact_name: str, object_id: str,
                             detail_payload: dict) -> RetrievalResult:
        artifact = str(detail_payload.get("name", artifact_name))
        source_name = str(detail_payload.get("museum", "")) or None
        source_url = str(detail_payload.get("detail_url", "")) or None

        field_map = {"artifact_dimensions_query": "dimensions"}
        field_name = field_map[template_name]
        value = detail_payload.get(field_name)
        if value in (None, ""):
            return RetrievalResult(status="no_data", fail_reason="知识图谱详情字段为空")

        raw_record = {
            "id": object_id, "artifact": artifact, field_name: str(value),
            "source_name": source_name, "source_url": source_url,
        }
        facts = [
            RetrievedFact(subject=artifact, predicate=field_name, object=str(value),
                          source_name=source_name, source_url=source_url),
        ]
        return RetrievalResult(status="ok", facts=facts, raw_records=[raw_record])

    def _build_author_result(self, artifact_name: str, object_id: str,
                             detail_payload: dict) -> RetrievalResult:
        artifact = str(detail_payload.get("name", artifact_name))
        source_name = str(detail_payload.get("museum", "")) or None
        source_url = str(detail_payload.get("detail_url", "")) or None
        artist = detail_payload.get("author") or detail_payload.get("artist")

        if not artist:
            return RetrievalResult(status="no_data", fail_reason="知识图谱中无作者信息")

        raw_record = {
            "id": object_id, "artifact": artifact, "artist": str(artist),
            "source_name": source_name, "source_url": source_url,
        }
        facts = [
            RetrievedFact(subject=artifact, predicate="artist", object=str(artist),
                          source_name=source_name, source_url=source_url),
        ]
        return RetrievalResult(status="ok", facts=facts, raw_records=[raw_record])

    # ── Same artist works (via search API) ──────────────────────

    def _query_same_artist_works(self, parameters: dict[str, object]) -> RetrievalResult | None:
        artist_name = str(parameters.get("artist_name", "")).strip()
        if not artist_name:
            return RetrievalResult(status="no_data", fail_reason="缺少作者名称")

        search_payload = self._get_json(
            f"/api/search?q={urllib.parse.quote(artist_name)}&page=1&page_size=10&lang=zh")
        items = search_payload.get("data", []) if isinstance(search_payload, dict) else []
        work_names = [str(item.get("name", "")) for item in items if item.get("name")]

        if not work_names:
            return (
                None if settings.graph_backend == "hybrid"
                else RetrievalResult(status="no_data", fail_reason="未找到该作者的其他作品")
            )

        source_name = str(items[0].get("museum", "")) if items else ""
        source_url = str(items[0].get("detail_url", "")) if items else ""

        raw_record = {
            "artist": artist_name,
            "works": work_names,
            "source_name": source_name or "中国海外流失文物知识图谱 API",
            "source_url": source_url or f"{settings.kg_api_base_url}/docs",
        }
        facts = [
            RetrievedFact(
                subject=artist_name,
                predicate="works",
                object="、".join(work_names),
                source_name=raw_record["source_name"],
                source_url=raw_record["source_url"],
            )
        ]
        return RetrievalResult(status="ok", facts=facts, raw_records=[raw_record])

    # ── Multi-hop (via /api/graph/neighbors/{id}) ──────────────

    def _query_multi_hop(self, parameters: dict[str, object]) -> RetrievalResult | None:
        artifact_name = str(parameters.get("artifact_name", "")).strip()
        if not artifact_name:
            return self._no_data_or_fallback("缺少文物名称")

        object_id = self._resolve_object_id(artifact_name)
        if not object_id:
            return self._no_data_or_fallback("知识图谱未命中文物")

        neighbors = self._get_json(f"/api/graph/neighbors/{object_id}?depth=2&limit=20&lang=zh")
        nodes = neighbors.get("nodes", []) if isinstance(neighbors, dict) else []
        links = neighbors.get("links", []) if isinstance(neighbors, dict) else []

        if not nodes:
            return self._no_data_or_fallback("未找到关联图数据")

        node_names = [str(n.get("name", n.get("id", "?"))) for n in nodes]
        relation_types = list({str(li.get("type", li.get("label", "?"))) for li in links})

        detail = self._get_json(f"/api/artifacts/{object_id}?lang=zh")
        artifact = str(detail.get("name", artifact_name))
        source_name = str(detail.get("museum", "中国海外流失文物知识图谱"))
        source_url = str(detail.get("detail_url", f"{settings.kg_api_base_url}/docs"))

        raw_record = {
            "artifact": artifact,
            "path_nodes": node_names,
            "path_relations": relation_types,
            "explanation": f"{artifact}的知识图谱关联路径为：{' → '.join(node_names)}。",
            "source_name": source_name,
            "source_url": source_url,
        }
        facts = [
            RetrievedFact(subject=artifact, predicate="graph_path", object=" → ".join(node_names),
                          source_name=source_name, source_url=source_url),
        ]
        return RetrievalResult(status="ok", facts=facts, raw_records=[raw_record])

    # ── Artifact comparison (via POST /api/artifacts/compare) ──

    def _query_compare_artifacts(self, parameters: dict[str, object]) -> RetrievalResult | None:
        names = parameters.get("artifact_names") or ([parameters.get("artifact_name")] if parameters.get("artifact_name") else [])
        if not names or len(names) < 2:
            # Only one artifact found? Try inferring second from the question pattern
            artifact_name = str(parameters.get("artifact_name", "")).strip()
            if not artifact_name:
                return self._no_data_or_fallback("对比至少需要两件文物名称")
            fallback = self._retrieve_from_mock("compare_artifacts_query")
            return fallback

        ids = []
        for name in names[:3]:
            oid = self._resolve_object_id(str(name).strip())
            if oid:
                ids.append(oid)
        if len(ids) < 2:
            return self._no_data_or_fallback("未能找到两件文物的ID")

        payload = json.dumps({"ids": ids}).encode()
        req = urllib.request.Request(
            f"{settings.kg_api_base_url}/api/artifacts/compare?lang=zh",
            data=payload, method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=settings.kg_api_timeout_seconds) as resp:
                data = json.loads(resp.read())
        except Exception:
            return self._no_data_or_fallback("文物对比接口调用失败")

        items = data.get("data", data.get("items", [])) if isinstance(data, dict) else []
        if not items:
            return self._no_data_or_fallback("对比接口返回为空")

        a1 = items[0] if len(items) > 0 else {}
        a2 = items[1] if len(items) > 1 else {}

        raw_record = {
            "artifact1": str(a1.get("name", names[0])),
            "artifact2": str(a2.get("name", names[1] if len(names) > 1 else "")),
            "dynasty1": str(a1.get("period", a1.get("dynasty", ""))),
            "dynasty2": str(a2.get("period", a2.get("dynasty", ""))),
            "material1": str(a1.get("material", "")),
            "material2": str(a2.get("material", "")),
            "museum1": str(a1.get("museum", "")),
            "museum2": str(a2.get("museum", "")),
            "dimensions1": str(a1.get("dimensions", a1.get("size", ""))),
            "dimensions2": str(a2.get("dimensions", a2.get("size", ""))),
            "source_name": str(a1.get("museum", "中国海外流失文物知识图谱")),
            "source_url": str(a1.get("detail_url", f"{settings.kg_api_base_url}/docs")),
        }
        facts = [
            RetrievedFact(
                subject=f"{raw_record['artifact1']} vs {raw_record['artifact2']}",
                predicate="comparison",
                object="已并排对比",
                source_name=raw_record["source_name"],
                source_url=raw_record["source_url"],
            )
        ]
        return RetrievalResult(status="ok", facts=facts, raw_records=[raw_record])

    # ── Artifact statistics (via /api/stats/distribution) ──────

    def _query_artifact_statistics(self, parameters: dict[str, object]) -> RetrievalResult | None:
        dynasty_name = str(parameters.get("dynasty_name", "")).strip()
        distribution = self._get_json("/api/stats/distribution")

        if not isinstance(distribution, dict):
            return self._no_data_or_fallback("统计接口返回为空")

        period_dist = distribution.get("period_distribution", distribution.get("periods", []))
        type_dist = distribution.get("type_distribution", distribution.get("types", []))
        material_dist = distribution.get("material_distribution", distribution.get("materials", []))
        museum_dist = distribution.get("museum_distribution", distribution.get("museums", []))

        total = sum(item.get("count", 0) for item in period_dist)
        types = [str(item.get("name", "")) for item in type_dist[:5] if item.get("name")]
        materials = [str(item.get("name", "")) for item in material_dist[:5] if item.get("name")]
        museums = [str(item.get("name", "")) for item in museum_dist[:5] if item.get("name")]

        display_dynasty = dynasty_name or "全部朝代"
        raw_record = {
            "dynasty": display_dynasty,
            "total_artifacts": total,
            "types": types,
            "materials": materials,
            "museums": museums,
            "source_name": "中国海外流失文物知识图谱",
            "source_url": f"{settings.kg_api_base_url}/docs",
        }
        facts = [
            RetrievedFact(subject=display_dynasty, predicate="total_artifacts", object=str(total),
                          source_name=raw_record["source_name"], source_url=raw_record["source_url"]),
        ]
        return RetrievalResult(status="ok", facts=facts, raw_records=[raw_record])

    # ── Graph path query (via /api/graph/path) ─────────────────

    def _query_graph_path(self, parameters: dict[str, object]) -> RetrievalResult | None:
        artifact_name = str(parameters.get("artifact_name", "")).strip()
        if not artifact_name:
            return self._no_data_or_fallback("缺少文物名称")

        object_id = self._resolve_object_id(artifact_name)
        if not object_id:
            return self._no_data_or_fallback("知识图谱未命中文物")

        # Use neighbors as a rich path-provenance view (path API needs two IDs)
        neighbors = self._get_json(f"/api/graph/neighbors/{object_id}?depth=2&limit=20&lang=zh")
        nodes = neighbors.get("nodes", []) if isinstance(neighbors, dict) else []
        links = neighbors.get("links", []) if isinstance(neighbors, dict) else []

        if not nodes:
            return self._no_data_or_fallback("未找到文物关联路径")

        node_names = [str(n.get("name", n.get("id", "?"))) for n in nodes]
        node_types = [str(n.get("type", n.get("label", ""))) for n in nodes]
        relation_types = list({str(li.get("type", li.get("label", "?"))) for li in links})

        detail = self._get_json(f"/api/artifacts/{object_id}?lang=zh")
        artifact = str(detail.get("name", artifact_name))
        source_name = str(detail.get("museum", "中国海外流失文物知识图谱"))
        source_url = str(detail.get("detail_url", f"{settings.kg_api_base_url}/docs"))

        raw_record = {
            "artifact": artifact,
            "path_nodes": node_names,
            "path_relations": relation_types,
            "node_types": node_types,
            "explanation": f"{artifact}的收藏与关联路径为：{' → '.join(node_names)}。",
            "source_name": source_name,
            "source_url": source_url,
        }
        facts = [
            RetrievedFact(subject=artifact, predicate="provenance_path", object=" → ".join(node_names),
                          source_name=source_name, source_url=source_url),
        ]
        return RetrievalResult(status="ok", facts=facts, raw_records=[raw_record])

    # ── Mock fallback ──────────────────────────────────────────

    def _retrieve_from_mock(self, template_name: str) -> RetrievalResult:
        records = MOCK_RESULTS.get(template_name, [])
        facts = []
        for record in records:
            for key, value in record.items():
                if key not in {"source_name", "source_url"}:
                    facts.append(RetrievedFact(
                        subject=record.get("artifact") or record.get("artist") or record.get("museum") or record.get("dynasty") or "result",
                        predicate=key,
                        object=str(value),
                        source_name=record.get("source_name"),
                        source_url=record.get("source_url"),
                    ))
        status = "ok" if records else "no_data"
        return RetrievalResult(status=status, facts=facts, raw_records=records,
                               fail_reason=None if records else "暂无相关数据")

    # ── Utility ────────────────────────────────────────────────

    def _no_data_or_fallback(self, reason: str) -> RetrievalResult | None:
        """Return no_data in remote mode, None in hybrid (triggers mock fallback)."""
        if settings.graph_backend == "hybrid":
            return None
        return RetrievalResult(status="no_data", fail_reason=reason)

    def _resolve_object_id(self, artifact_name: str) -> str | None:
        payload = self._get_json(
            f"/api/search?q={urllib.parse.quote(artifact_name)}&page=1&page_size=10&lang=zh")
        candidates = payload.get("data", []) if isinstance(payload, dict) else []
        if not candidates:
            return None
        normalized_target = self._normalize_text(artifact_name)
        exact_match = next(
            (item for item in candidates
             if self._normalize_text(str(item.get("name", ""))) == normalized_target),
            None,
        )
        selected = exact_match or candidates[0]
        return str(selected.get("id")) if selected.get("id") is not None else None

    def _get_json(self, path: str) -> dict:
        base_url = settings.kg_api_base_url.rstrip("/")
        request = urllib.request.Request(f"{base_url}{path}", method="GET")
        with urllib.request.urlopen(request, timeout=settings.kg_api_timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8", errors="replace"))

    def _normalize_text(self, value: str) -> str:
        return unescape(value).replace("�", "-").strip().lower()
