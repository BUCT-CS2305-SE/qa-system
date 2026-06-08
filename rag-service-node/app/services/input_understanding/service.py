from __future__ import annotations

import re

from app.models.domain import EntityMention, UnderstandingResult
from app.services.input_understanding.context_resolver import ContextResolver
from app.services.input_understanding.entity_extractor import EntityExtractor
from app.services.input_understanding.intent_classifier import IntentClassifier
from app.services.input_understanding.normalizer import QuestionNormalizer


class InputUnderstandingService:
    def __init__(self, context_resolver: ContextResolver | None = None) -> None:
        self.normalizer = QuestionNormalizer()
        self.entity_extractor = EntityExtractor()
        self.intent_classifier = IntentClassifier()
        self.context_resolver = context_resolver or ContextResolver()

    def understand(self, question: str, session_id: str | None = None) -> UnderstandingResult:
        normalized = self.normalizer.normalize(question)
        entities = self.entity_extractor.extract(normalized)
        intent, confidence, template_name = self.intent_classifier.classify(normalized, entities)
        entities, _topic_switched = self.context_resolver.resolve(normalized, entities, intent, session_id)
        entities = self._infer_missing_entities(normalized, intent, entities)
        intent, template_name = self._align_intent_to_entities(normalized, intent, entities, template_name)
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

    def _align_intent_to_entities(self, normalized: str, intent: str, entities: dict[str, list[EntityMention]], template_name: str | None) -> tuple[str, str | None]:
        artifact_intents = {
            "artifact_museum",
            "artifact_period",
            "artifact_material",
            "artifact_type",
            "artifact_description",
            "artifact_dimensions",
            "recommended_artifacts",
            "painting_author",
            "multi_hop",
            "path_query",
            "compare_artifacts",
        }
        artist_intents = {"artist_biography", "same_artist_works"}
        dynasty_intents = {"artifact_statistics", "dynasty_representative_artifacts"}

        if intent in artifact_intents and not entities.get("artifact"):
            if entities.get("museum"):
                alt_intent, _, alt_template = self.intent_classifier.classify(normalized, entities)
                if alt_intent != "unknown" and alt_intent not in artifact_intents:
                    return alt_intent, alt_template
            if entities.get("dynasty"):
                alt_intent, _, alt_template = self.intent_classifier.classify(normalized, entities)
                if alt_intent != "unknown" and alt_intent not in artifact_intents:
                    return alt_intent, alt_template
            if entities.get("artist"):
                alt_intent, _, alt_template = self.intent_classifier.classify(normalized, entities)
                if alt_intent != "unknown" and alt_intent not in artifact_intents:
                    return alt_intent, alt_template

        if intent in artist_intents and not entities.get("artist"):
            if entities.get("dynasty"):
                alt_intent, _, alt_template = self.intent_classifier.classify(normalized, entities)
                if alt_intent != "unknown" and alt_intent not in artist_intents:
                    return alt_intent, alt_template

        if intent in dynasty_intents and not entities.get("dynasty"):
            if entities.get("artifact"):
                alt_intent, _, alt_template = self.intent_classifier.classify(normalized, entities)
                if alt_intent != "unknown" and alt_intent not in dynasty_intents:
                    return alt_intent, alt_template

        if intent == "museum_count" and not entities.get("museum"):
            if entities.get("dynasty"):
                alt_intent, _, alt_template = self.intent_classifier.classify(normalized, entities)
                if alt_intent != "unknown" and alt_intent != "museum_count":
                    return alt_intent, alt_template

        return intent, template_name

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
            "multi_hop",
            "path_query",
            "compare_artifacts",
        }
        artist_intents = {"artist_biography", "same_artist_works"}
        dynasty_intents = {"artifact_statistics", "dynasty_representative_artifacts"}

        if intent in artifact_intents and not entities.get("artifact"):
            likely_type = self._detect_entity_type_hint(normalized)
            if likely_type == "museum" and not entities.get("museum"):
                inferred = self._infer_museum_entity(normalized, entities)
                if inferred.get("museum"):
                    return inferred
            if likely_type == "artist" and not entities.get("artist"):
                inferred = self._infer_artist_entity(normalized, entities, intent)
                if inferred.get("artist"):
                    return inferred
            if likely_type == "dynasty" and not entities.get("dynasty"):
                inferred = self._infer_dynasty_entity(normalized, entities, intent)
                if inferred.get("dynasty"):
                    return inferred
            if entities.get("museum") or entities.get("artist") or entities.get("dynasty"):
                return entities
            return self._infer_artifact_entity(normalized, entities, intent)

        if intent in artist_intents and not entities.get("artist"):
            return self._infer_artist_entity(normalized, entities, intent)

        if intent == "museum_count" and not entities.get("museum"):
            return self._infer_museum_entity(normalized, entities)

        if intent in dynasty_intents and not entities.get("dynasty"):
            return self._infer_dynasty_entity(normalized, entities, intent)

        return entities

    def _detect_entity_type_hint(self, text: str) -> str | None:
        if any(w in text for w in ["博物馆", "博物院", "museum", "Museum"]):
            return "museum"
        if any(w in text for w in ["朝", "代", "Dynasty", "dynasty", "时期"]):
            return "dynasty"
        if any(w in text for w in ["作者", "画家", "艺术家", "artist", "Artist"]):
            return "artist"
        return None

    _COMMON_PREFIX_PATTERNS = [
        r"^介绍一下\s*",
        r"^请介绍\s*",
        r"^介绍\s*",
        r"^什么是\s*",
        r"^是什么\s*",
    ]

    def _strip_common_prefixes(self, text: str) -> str:
        for pattern in self._COMMON_PREFIX_PATTERNS:
            text = re.sub(pattern, "", text)
        return text.strip()

    _INTENT_KEYWORD_STRIP: dict[str, list[str]] = {
        "artifact_museum": ["museum", "which museum", "where is", "collection of", "located in"],
        "artifact_period": ["period", "dynasty", "when was", "era"],
        "artifact_material": ["material", "made of", "what is.*made"],
        "artifact_type": ["type", "category", "what kind"],
        "artifact_description": ["description", "describe", "tell me about", "what is"],
        "artifact_dimensions": ["dimensions", "size", "weight", "measurement"],
        "painting_author": ["author", "artist of", "who painted", "who created", "who made"],
        "museum_count": ["count", "how many", "collection size", "how much"],
        "recommended_artifacts": ["related", "recommend", "similar", "like this"],
        "dynasty_representative_artifacts": ["representative", "artifacts of", "artifacts from"],
        "artist_biography": ["biography", "life of", "who is", "tell me about"],
        "same_artist_works": ["other works", "same artist", "also painted", "also created", "more by", "works by", "同作者", "作品"],
    }

    def _strip_english_keywords(self, text: str, intent: str) -> str:
        for kw in self._INTENT_KEYWORD_STRIP.get(intent, []):
            text = re.sub(rf"\s*\b{re.escape(kw)}\b\s*", " ", text, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", text)

    def _infer_artifact_entity(self, normalized: str, entities: dict[str, list[EntityMention]], intent: str = "") -> dict[str, list[EntityMention]]:
        if entities.get("artifact"):
            return entities

        if self._detect_entity_type_hint(normalized) is not None:
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
            r"在哪里\??$",
            r"在哪儿\??$",
            r"在哪\??$",
            r"在哪个博物馆\??$",
            r"现藏于\??$",
            r"藏于\??$",
            r"收藏于\??$",
        ]
        for pattern in artifact_patterns:
            candidate = re.sub(pattern, "", candidate)

        candidate = self._strip_common_prefixes(candidate)
        candidate = candidate.strip(" ?,.，。；：!！")
        candidate = self._strip_english_keywords(candidate, intent)
        if not candidate or self._detect_entity_type_hint(candidate) is not None:
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

    def _infer_artist_entity(self, normalized: str, entities: dict[str, list[EntityMention]], intent: str = "") -> dict[str, list[EntityMention]]:
        candidate = normalized
        artist_patterns = [
            r"同作者的作品有哪些\??$",
            r"还有哪些作品\??$",
            r"还画了什么\??$",
            r"还创作了什么\??$",
            r"的生平经历是怎样的\??$",
            r"的生平是怎样的\??$",
            r"是谁\??$",
            r"的生平\??$",
            r"的介绍\??$",
        ]
        for pattern in artist_patterns:
            candidate = re.sub(pattern, "", candidate)

        candidate = self._strip_common_prefixes(candidate)
        candidate = candidate.strip(" ?,.。，；：!！")
        candidate = self._strip_english_keywords(candidate, intent)
        if not candidate or self._detect_entity_type_hint(candidate) == "museum":
            return entities

        inferred_entities = dict(entities)
        inferred_entities["artist"] = [
            EntityMention(
                entity_type="artist",
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

        candidate = self._strip_common_prefixes(candidate)
        candidate = candidate.strip(" ?,.，。；：!！")
        candidate = self._strip_english_keywords(candidate, "museum_count")
        if not candidate or self._detect_entity_type_hint(candidate) == "dynasty":
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

    _PRONOUN_TOKENS = {"它", "他", "她", "其", "这个", "那个", "这件", "那件", "这些", "那些", "该文物"}

    def _infer_dynasty_entity(self, normalized: str, entities: dict[str, list[EntityMention]], intent: str = "") -> dict[str, list[EntityMention]]:
        candidate = normalized
        dynasty_patterns = [
            r"的代表性文物有哪些\??$",
            r"有哪些(代表)?文物\??$",
            r"统计\??$",
            r"分布\??$",
            r"哪个朝代\??$",
            r"什么朝代\??$",
        ]
        for pattern in dynasty_patterns:
            candidate = re.sub(pattern, "", candidate)

        candidate = self._strip_common_prefixes(candidate)
        candidate = candidate.strip(" ?,.。，；：!！")
        candidate = self._strip_english_keywords(candidate, intent)
        if not candidate or self._detect_entity_type_hint(candidate) == "museum":
            return entities

        inferred_entities = dict(entities)
        inferred_entities["dynasty"] = [
            EntityMention(
                entity_type="dynasty",
                canonical_name=candidate,
                matched_text=candidate,
                confidence=0.65,
            )
        ]
        return inferred_entities