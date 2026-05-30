from __future__ import annotations

import re

from app.models.domain import EntityMention, UnderstandingResult
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
        entities = self._infer_missing_entities(normalized, intent, entities)
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

    def _infer_missing_entities(self, normalized: str, intent: str, entities: dict[str, list[EntityMention]]) -> dict[str, list[EntityMention]]:
        artifact_intents = {
            "artifact_museum",
            "artifact_period",
            "artifact_material",
            "artifact_type",
            "artifact_description",
            "artifact_dimensions",
            "recommended_artifacts",
            "painting_author",
        }
        if intent in artifact_intents and not entities.get("artifact"):
            return self._infer_artifact_entity(normalized, entities)

        if intent == "museum_count" and not entities.get("museum"):
            return self._infer_museum_entity(normalized, entities)

        return entities

    def _infer_artifact_entity(self, normalized: str, entities: dict[str, list[EntityMention]]) -> dict[str, list[EntityMention]]:
        if entities.get("artifact"):
            return entities

        candidate = normalized
        artifact_patterns = [
            r"现藏于哪家博物馆\??$",
            r"收藏于哪\??$",
            r"属于哪个历史时期\??$",
            r"属于哪个朝代\??$",
            r"由什么材料制成\??$",
            r"什么材料制成\??$",
            r"是什么材质\??$",
            r"什么材质\??$",
            r"是什么类型\??$",
            r"是什么类别\??$",
            r"什么类型\??$",
            r"什么类别\??$",
            r"哪种器物\??$",
            r"属于什么类型\??$",
            r"介绍一下\??$",
            r"请介绍\??$",
            r"是什么文物\??$",
            r"是什么\??$",
            r"的尺寸和重量是多少\??$",
            r"的尺寸是多少\??$",
            r"尺寸和重量是多少\??$",
            r"尺寸是多少\??$",
            r"规格是多少\??$",
            r"多大\??$",
            r"重量是多少\??$",
            r"推荐(一些|几个|几件)?(相关|类似)?文物\??$",
            r"有(哪些|什么)推荐\??$",
            r"还有哪些文物推荐\??$",
            r"还有什么文物推荐\??$",
            r"还有什么文物推荐\??$",
            r"还有哪些文物\??$",
            r"相关文物有哪些\??$",
            r"类似文物有哪些\??$",
            r"的作者是谁\??$",
            r"作者是谁\??$",
            r"谁画的\??$",
            r"谁创作的\??$",
        ]
        for pattern in artifact_patterns:
            candidate = re.sub(pattern, "", candidate)

        candidate = candidate.strip(" ?,.，。；：!！")
        if not candidate:
            return entities

        inferred_entities = dict(entities)
        inferred_entities["artifact"] = [
            EntityMention(
                entity_type="artifact",
                canonical_name=candidate,
                matched_text=candidate,
                confidence=0.65,
            )
        ]
        return inferred_entities

    def _infer_museum_entity(self, normalized: str, entities: dict[str, list[EntityMention]]) -> dict[str, list[EntityMention]]:
        candidate = normalized
        museum_patterns = [
            r"收藏了多少件中国文物\??$",
            r"一共有多少件中国文物\??$",
            r"有多少件中国文物\??$",
            r"收藏了多少件\??$",
            r"一共有多少件\??$",
            r"有多少件\??$",
        ]
        for pattern in museum_patterns:
            candidate = re.sub(pattern, "", candidate)

        candidate = candidate.strip(" ?,.，。；：!！")
        if not candidate:
            return entities

        inferred_entities = dict(entities)
        inferred_entities["museum"] = [
            EntityMention(
                entity_type="museum",
                canonical_name=candidate,
                matched_text=candidate,
                confidence=0.65,
            )
        ]
        return inferred_entities