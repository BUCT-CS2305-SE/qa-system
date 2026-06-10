from __future__ import annotations

import re
import time
from collections import defaultdict

from app.core.config import settings
from app.models.domain import EntityMention

_PRONOUN_PATTERNS = [
    re.compile(p)
    for p in [
        r"^(它|他|她|其)(的|属于|是|在|有|的)?",
        r"^(这个|那个|这件|那件|这些|那些)(的|属于|是|在|有|的)?",
        r"^(该文物|这件文物|那件文物|这个文物|那个文物)",
        r"^(上文|上面|前面)(提到的)?(文物|作品|这个)?",
    ]
]

_TOPIC_SWITCH_SIGNALS = [
    re.compile(p)
    for p in [
        r"(换一个|换个话题|不说这个|另一个|别的|其他)",
        r"^(那|那好|对了|哦还有|另外).*(问|说|讲|介绍|查|看)",
    ]
]

_ENTITY_TYPE_HINT_WORDS = ["博物馆", "博物院", "museum", "Museum", "朝代", "dynasty", "Dynasty"]


class ContextResolver:
    _SESSION_TTL_SECONDS = 30 * 60

    def __init__(self) -> None:
        self._history: dict[str, list[dict]] = defaultdict(list)

    def resolve(
        self,
        current_question: str,
        entities: dict[str, list[EntityMention]],
        intent: str,
        session_id: str | None,
    ) -> tuple[dict[str, list[EntityMention]], bool]:
        """Resolve context references. Returns (entities, topic_switched)."""
        if not session_id:
            return entities, False

        self._expire_old_entries(session_id)
        recent = self._history.get(session_id, [])
        if not recent:
            return entities, False

        topic_switched = self._detect_topic_switch(current_question, intent, recent)

        if topic_switched:
            self._history[session_id] = []
            return entities, True

        if self._is_pronoun_question(current_question):
            inherited = self._inherit_entity_from_history(recent)
            if inherited and not entities:
                return inherited, False
            if inherited:
                for etype, mentions in inherited.items():
                    if etype not in entities:
                        entities[etype] = mentions

        elif not entities:
            inherited = self._inherit_entity_from_history(recent)
            if inherited and not self._question_introduces_new_entity(current_question, recent):
                entities = inherited

        return entities, False

    def record_turn(
        self,
        session_id: str,
        role: str,
        question: str,
        extracted: dict[str, str],
        intent: str = "",
    ) -> None:
        if not session_id:
            return
        entry = {
            "role": role,
            "text": question,
            "intent": intent,
            "ts": time.time(),
            **extracted,
        }
        self._history[session_id].append(entry)
        cap = settings.context_window * 2
        if len(self._history[session_id]) > cap:
            self._history[session_id] = self._history[session_id][-cap:]

    def get_recent(self, session_id: str | None, limit: int | None = None) -> list[dict]:
        if not session_id:
            return []
        self._expire_old_entries(session_id)
        recent = self._history.get(session_id, [])
        if limit:
            return recent[-limit:]
        return recent[-settings.context_window * 2 :]

    def clear_session(self, session_id: str) -> None:
        self._history.pop(session_id, None)

    def _detect_topic_switch(self, question: str, intent: str, recent: list[dict]) -> bool:
        for pattern in _TOPIC_SWITCH_SIGNALS:
            if pattern.search(question):
                return True

        last_user = None
        for entry in reversed(recent):
            if entry.get("role") == "user":
                last_user = entry
                break

        if last_user:
            last_intent = last_user.get("intent", "")
            if last_intent and intent and last_intent != intent:
                last_entities = {
                    k: v for k, v in last_user.items() if k in ("artifact", "artist", "museum", "dynasty") and v
                }
                current_entities = any(
                    entry.get(k) and entry.get(k, "") in (last_entities.get(k) or "")
                    for entry in recent[-2:]
                    for k in ("artifact", "artist", "museum", "dynasty")
                )
                if not current_entities and intent not in ("unknown", "chat"):
                    return True

        return False

    def _is_pronoun_question(self, question: str) -> bool:
        text = question.strip()
        for pattern in _PRONOUN_PATTERNS:
            if pattern.search(text):
                return True
        return len(text) <= 6 and any(w in text for w in ("它", "他", "她", "这个", "那个", "这件", "那些", "这些"))

    def _inherit_entity_from_history(self, recent: list[dict]) -> dict[str, list[EntityMention]] | None:
        for entry in reversed(recent):
            if entry.get("role") == "assistant":
                for key in ("artifact", "artist", "museum", "dynasty"):
                    val = entry.get(key)
                    if val:
                        return {
                            key: [EntityMention(entity_type=key, canonical_name=val, matched_text=val, confidence=0.7)]
                        }
                break
        return None

    def _question_introduces_new_entity(self, question: str, recent: list[dict]) -> bool:
        question_lower = question.lower()
        hist_names: set[str] = set()
        for entry in recent:
            for key in ("artifact", "artist", "museum", "dynasty"):
                val = entry.get(key)
                if val:
                    hist_names.add(val.lower())
        for name in hist_names:
            if name in question_lower:
                return False
        return any(word.lower() in question_lower for word in _ENTITY_TYPE_HINT_WORDS)

    def _expire_old_entries(self, session_id: str) -> None:
        now = time.time()
        cutoff = now - self._SESSION_TTL_SECONDS
        entries = self._history.get(session_id, [])
        if not entries:
            return
        fresh = [e for e in entries if e.get("ts", now) > cutoff]
        if len(fresh) != len(entries):
            self._history[session_id] = fresh
