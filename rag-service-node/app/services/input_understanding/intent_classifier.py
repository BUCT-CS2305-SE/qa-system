from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple


class IntentClassifier:
    def __init__(self) -> None:
        rule_path = Path(__file__).resolve().parents[2] / "config" / "intent_rules.json"
        self.rules = json.loads(rule_path.read_text(encoding="utf-8"))

    def classify(self, question: str, entities: Dict[str, List[object]]) -> Tuple[str, float, str | None]:
        scores: List[Tuple[str, float, str | None]] = []
        for rule in self.rules:
            score = 0.0
            for keyword in rule["keywords"]:
                if keyword in question:
                    score = max(score, 0.85)
            if score > 0:
                required_entity = rule.get("required_entity")
                if required_entity and required_entity in entities:
                    score += 0.1
                scores.append((rule["intent"], min(score, 0.99), rule.get("template_name")))
        if not scores:
            return "unknown", 0.0, None
        scores.sort(key=lambda item: item[1], reverse=True)
        return scores[0]