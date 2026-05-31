from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from app.core.config import settings
from app.models.domain import EntityMention


class ContextResolver:
    def __init__(self) -> None:
        self._history: dict[str, list[dict[str, str]]] = defaultdict(list)

    def resolve(self, current_question: str, entities: Dict[str, List[EntityMention]], session_id: str | None) -> Dict[str, List[EntityMention]]:
        if not session_id:
            return entities

        recent = self._history.get(session_id, [])
        if recent:
            last_artifact = None
            for entry in reversed(recent):
                if entry.get("role") == "assistant":
                    for key in ("artifact", "artist", "museum", "dynasty"):
                        val = entry.get(key)
                        if val:
                            last_artifact = (key, val)
                            break
                    if last_artifact:
                        break

            if last_artifact and not entities:
                entity_type, name = last_artifact
                entities[entity_type] = [
                    EntityMention(entity_type=entity_type, canonical_name=name, matched_text=name, confidence=0.7)
                ]

        return entities

    def record_turn(self, session_id: str, role: str, question: str, extracted: dict[str, str]) -> None:
        if not session_id:
            return
        entry = {"role": role, "text": question, **extracted}
        self._history[session_id].append(entry)
        if len(self._history[session_id]) > settings.context_window * 2:
            self._history[session_id] = self._history[session_id][-settings.context_window * 2:]

    def get_recent(self, session_id: str | None, limit: int | None = None) -> list[dict[str, str]]:
        if not session_id:
            return []
        recent = self._history.get(session_id, [])
        if limit:
            return recent[-limit:]
        return recent[-settings.context_window * 2:]
