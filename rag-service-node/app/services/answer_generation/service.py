from __future__ import annotations

from app.models.domain import GeneratedAnswer, RetrievalResult, UnderstandingResult


class AnswerGenerationService:
    def generate(self, understanding: UnderstandingResult, retrieval: RetrievalResult) -> GeneratedAnswer:
        if retrieval.status != "ok" or not retrieval.raw_records:
            return GeneratedAnswer(answer="暂无相关数据", source=[], confidence=0.0)

        record = retrieval.raw_records[0]
        answer = self._build_answer(understanding.intent, record)
        source = []
        if record.get("source_name") and record.get("source_url"):
            source.append({"name": record["source_name"], "url": record["source_url"]})
        return GeneratedAnswer(
            answer=answer,
            source=source,
            llm_note="当前为规则版答案组织，后续可替换为 RAG 生成。",
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
        if intent == "museum_count":
            return f"{record['museum']}共收藏了{record['artifact_count']}件中国文物。"
        if intent == "recommended_artifacts":
            recommendations = record.get("recommendations", [])
            if isinstance(recommendations, list) and recommendations:
                return f"如果你关注{record['artifact']}，还可以继续了解：{'、'.join(str(item) for item in recommendations)}。"
        return "已检索到相关事实。"