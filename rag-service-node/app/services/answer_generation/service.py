from __future__ import annotations

from app.core.config import settings
from app.models.domain import GeneratedAnswer, RetrievalResult, UnderstandingResult
from app.services.llm.service import LlmService


class AnswerGenerationService:
    def __init__(self) -> None:
        self._llm: LlmService | None = None

    @property
    def llm(self) -> LlmService:
        if self._llm is None:
            self._llm = LlmService()
        return self._llm

    def generate(
        self,
        understanding: UnderstandingResult,
        retrieval: RetrievalResult,
        mode: str = "rule",
    ) -> GeneratedAnswer:
        if retrieval.status != "ok" or not retrieval.raw_records:
            return GeneratedAnswer(answer="暂无相关数据", source=[], confidence=0.0)

        record = retrieval.raw_records[0]
        try:
            artifact_display = (
                understanding.entities["artifact"][0].canonical_name
                if understanding.entities and "artifact" in understanding.entities
                else record.get("artifact")
            )
        except Exception:
            artifact_display = record.get("artifact")
        record_for_answer = dict(record)
        if artifact_display and artifact_display != record.get("artifact"):
            record_artifact = record.get("artifact")
            if isinstance(record_artifact, str) and isinstance(artifact_display, str):
                norm_record = record_artifact.strip().lower()
                norm_display = artifact_display.strip().lower()
                if norm_record not in norm_display and norm_display not in norm_record:
                    artifact_display = record_artifact
        if artifact_display:
            record_for_answer["artifact"] = artifact_display

        source = []
        if record.get("source_name") and record.get("source_url"):
            source.append({"name": record["source_name"], "url": record["source_url"]})

        use_llm = mode in {"auto", "llm"}

        if use_llm and settings.llm_available:
            try:
                fact_dicts = [f.model_dump() for f in retrieval.facts]
                source_dicts = [
                    {"source_name": f.source_name, "detail_url": f.source_url}
                    for f in retrieval.facts
                    if f.source_name or f.source_url
                ]
                polished = self.llm.generate(understanding.normalized_question, fact_dicts, source_dicts)
                return GeneratedAnswer(
                    answer=polished,
                    source=source,
                    llm_note=f"本回答由 {settings.llm_model} 基于知识图谱事实生成，关键事实已核实。",
                    confidence=understanding.confidence,
                )
            except Exception as exc:
                if mode == "llm":
                    return GeneratedAnswer(answer="暂无相关数据", source=[], confidence=0.0)
                # auto mode: fall through to rule-based answer

        answer = self._build_answer(understanding.intent, record_for_answer)
        return GeneratedAnswer(
            answer=answer,
            source=source,
            llm_note="当前为规则版答案组织。如需 LLM 润色，请配置 qa_llm_api_url 环境变量并使用 mode=auto。",
            confidence=understanding.confidence,
        )

    def _build_answer(self, intent: str, record: dict[str, object]) -> str:
        if intent == "artifact_museum":
            return f"{record['artifact']}现藏于{record['museum']}。"
        if intent == "artifact_period":
            return f"{record['artifact']}所属历史时期为{record['dynasty']}。"
        if intent == "artifact_material":
            return f"{record['artifact']}的材质为{record['material']}。"
        if intent == "artifact_type":
            return f"{record['artifact']}属于{record['type']}类型。"
        if intent == "artifact_description":
            desc = record.get("description")
            if desc and str(desc).strip():
                return f"{record['artifact']}的介绍如下：{record['description']}"
            parts = [f"{record['artifact']}的基本信息："]
            if record.get("type") and str(record["type"]).strip() and str(record["type"]).strip() != "未知":
                parts.append(f"类型为{record['type']}")
            if record.get("material") and str(record["material"]).strip() and str(record["material"]).strip() != "未知":
                parts.append(f"材质为{record['material']}")
            if record.get("period") or record.get("dynasty"):
                p = record.get("period") or record.get("dynasty")
                if p and str(p).strip():
                    parts.append(f"所属时期为{p}")
            if record.get("dimensions") and str(record["dimensions"]).strip():
                parts.append(f"尺寸为{record['dimensions']}")
            if record.get("museum") or record.get("source_name"):
                m = record.get("museum") or record.get("source_name")
                if m and str(m).strip():
                    parts.append(f"现藏于{m}")
            if len(parts) == 1:
                return f"{record['artifact']}的详细信息暂无。"
            return "。".join(parts) + "。"
        if intent == "artifact_dimensions":
            return f"{record['artifact']}的尺寸信息为{record['dimensions']}。"
        if intent == "painting_author":
            return f"{record['artifact']}的作者是{record['artist']}。"
        if intent == "artist_biography":
            return f"关于{record.get('artist', '该作者')}：{record.get('biography', '暂无生平信息')}"
        if intent == "museum_count":
            return f"{record['museum']}共收藏了{record['artifact_count']}件中国文物。"
        if intent == "dynasty_representative_artifacts":
            artifacts = record.get("artifacts", [])
            if isinstance(artifacts, list) and artifacts:
                return f"{record['dynasty']}的代表性文物有：{'、'.join(str(a) for a in artifacts)}。"
            return f"{record['dynasty']}的相关文物信息暂无。"
        if intent == "recommended_artifacts":
            recommendations = record.get("recommendations", [])
            if isinstance(recommendations, list) and recommendations:
                return f"如果你关注{record['artifact']}，还可以继续了解：{'、'.join(str(item) for item in recommendations)}。"
        if intent == "same_artist_works":
            works = record.get("works", [])
            if isinstance(works, list) and works:
                return f"{record['artist']}的其他作品有：{'、'.join(str(w) for w in works)}。"
            return f"{record.get('artist', '该作者')}的其他作品信息暂无。"
        if intent == "multi_hop":
            nodes = record.get("path_nodes", [])
            if isinstance(nodes, list) and nodes:
                explanation = record.get("explanation", f"流转路径：{' → '.join(str(n) for n in nodes)}")
                return str(explanation)
            return f"{record['artifact']}的流转路径暂无详细信息。"
        if intent == "compare_artifacts":
            parts = []
            a1 = record.get("artifact1", "文物一")
            a2 = record.get("artifact2", "文物二")
            parts.append(f"{a1}与{a2}的比较如下：")
            if record.get("dynasty1") and record.get("dynasty2"):
                parts.append(f"年代：{a1}为{record['dynasty1']}，{a2}为{record['dynasty2']}")
            if record.get("material1") and record.get("material2"):
                parts.append(f"材质：{a1}为{record['material1']}，{a2}为{record['material2']}")
            if record.get("museum1") and record.get("museum2"):
                parts.append(f"收藏地：{a1}在{record['museum1']}，{a2}在{record['museum2']}")
            if record.get("dimensions1") and record.get("dimensions2"):
                parts.append(f"尺寸：{a1}为{record['dimensions1']}，{a2}为{record['dimensions2']}")
            return "。".join(parts) + "。"
        if intent == "artifact_statistics":
            total = record.get("total_artifacts", 0)
            parts = [f"{record.get('dynasty', '该朝代')}共有{total}件文物。"]
            types = record.get("types", [])
            if isinstance(types, list) and types:
                parts.append(f"类型包括：{'、'.join(str(t) for t in types)}")
            materials = record.get("materials", [])
            if isinstance(materials, list) and materials:
                parts.append(f"材质包括：{'、'.join(str(m) for m in materials)}")
            museums = record.get("museums", [])
            if isinstance(museums, list) and museums:
                parts.append(f"分布于以下博物馆：{'、'.join(str(m) for m in museums)}")
            return "。".join(parts) + "。"
        if intent == "path_query":
            nodes = record.get("path_nodes", [])
            if isinstance(nodes, list) and nodes:
                explanation = record.get("explanation", f"路径：{' → '.join(str(n) for n in nodes)}")
                return str(explanation)
            return f"{record['artifact']}的收藏路径暂无详细信息。"
        return "已检索到相关事实。"