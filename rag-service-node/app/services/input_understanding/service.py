from __future__ import annotations

from app.models.domain import UnderstandingResult
from app.services.input_understanding.context_resolver import ContextResolver
from app.services.input_understanding.entity_extractor import EntityExtractor
from app.services.input_understanding.intent_classifier import IntentClassifier
from app.services.input_understanding.normalizer import QuestionNormalizer


class InputUnderstandingService:
    def __init__(self) -> None:
        self.normalizer = QuestionNormalizer()
        self.entity_extractor = EntityExtractor()
        self.intent_classifier = IntentClassifier()
        self.context_resolver = ContextResolver()

    def understand(self, question: str, session_id: str | None = None) -> UnderstandingResult:
        normalized = self.normalizer.normalize(question)
        entities = self.entity_extractor.extract(normalized)
        entities = self.context_resolver.resolve(normalized, entities, session_id)
        intent, confidence, template_name = self.intent_classifier.classify(normalized, entities)
        if intent == "unknown":
            return UnderstandingResult(
                normalized_question=normalized,
                intent=intent,
                entities=entities,
                confidence=confidence,
                status="clarify",
                fail_reason="未识别问题意图",
                constraints={},
            )
        constraints = {}
        if template_name:
            constraints["template_name"] = template_name
        return UnderstandingResult(
            normalized_question=normalized,
            intent=intent,
            entities=entities,
            constraints=constraints,
            confidence=confidence,
        )