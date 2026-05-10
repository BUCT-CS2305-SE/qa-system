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
        if intent == "painting_author":
            return f"{record['artifact']}的作者是{record['artist']}。"
        if intent == "museum_count":
            return f"{record['museum']}共收藏了{record['artifact_count']}件中国文物。"
        return "已检索到相关事实。"