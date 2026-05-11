from __future__ import annotations

from app.models.domain import RetrievalResult, RetrievedFact
from app.services.kg_retrieval.mock_data import MOCK_RESULTS


class KGRetrievalService:
    def retrieve(self, template_name: str | None, query_text: str | None, parameters: dict[str, object]) -> RetrievalResult:
        if not template_name or not query_text:
            return RetrievalResult(status="no_data", fail_reason="未生成查询语句")

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