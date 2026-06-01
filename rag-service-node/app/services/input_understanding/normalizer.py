import re


class QuestionNormalizer:
    def normalize(self, question: str) -> str:
        normalized = question.strip().replace("？", "?").replace("，", ",")
        normalized = normalized.replace("请问", "").replace("一下", "")
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized