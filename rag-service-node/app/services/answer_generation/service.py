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
            return f"{record['artifact']}的介绍如下：{record['description']}"
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
        return "已检索到相关事实。"