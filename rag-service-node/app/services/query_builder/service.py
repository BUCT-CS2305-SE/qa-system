from __future__ import annotations

from app.models.domain import QueryPlan, UnderstandingResult
from app.services.query_builder.templates import QUERY_TEMPLATES


class QueryBuilderService:
    def build(self, understanding: UnderstandingResult) -> QueryPlan:
        template_name = understanding.constraints.get("template_name")
        if not template_name:
            return QueryPlan(template_name=None, query_text=None, parameters={})

        parameters = {}
        if "artifact" in understanding.entities:
            parameters["artifact_name"] = understanding.entities["artifact"][0].canonical_name
        if "artist" in understanding.entities:
            parameters["artist_name"] = understanding.entities["artist"][0].canonical_name
        if "dynasty" in understanding.entities:
            parameters["dynasty_name"] = understanding.entities["dynasty"][0].canonical_name
        if "museum" in understanding.entities:
            parameters["museum_name"] = understanding.entities["museum"][0].canonical_name

        return QueryPlan(
            backend="cypher",
            template_name=template_name,
            query_text=QUERY_TEMPLATES.get(template_name),
            parameters=parameters,
        )