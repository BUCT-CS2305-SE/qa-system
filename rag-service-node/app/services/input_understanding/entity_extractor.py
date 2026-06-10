from __future__ import annotations

import json
from pathlib import Path

from app.models.domain import EntityMention


class EntityExtractor:
    def __init__(self) -> None:
        kb_path = Path(__file__).resolve().parents[2] / "config" / "entity_aliases.json"
        self.entity_kb = json.loads(kb_path.read_text(encoding="utf-8"))

    def extract(self, question: str) -> dict[str, list[EntityMention]]:
        entities: dict[str, list[EntityMention]] = {}
        for entity_type, records in self.entity_kb.items():
            matches: list[EntityMention] = []
            for record in records:
                for alias in record["aliases"]:
                    if alias in question:
                        matches.append(
                            EntityMention(
                                entity_type=entity_type,
                                canonical_name=record["canonical_name"],
                                matched_text=alias,
                                confidence=0.95,
                            )
                        )
                        break
            if matches:
                entities[entity_type] = matches
        return entities
