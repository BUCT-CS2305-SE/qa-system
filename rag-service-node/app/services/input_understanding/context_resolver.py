from __future__ import annotations

from typing import Dict, List

from app.models.domain import EntityMention


class ContextResolver:
    def resolve(self, current_question: str, entities: Dict[str, List[EntityMention]], session_id: str | None) -> Dict[str, List[EntityMention]]:
        return entities