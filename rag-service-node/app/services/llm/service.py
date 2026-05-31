from __future__ import annotations

import json
import urllib.request
from typing import Any, Dict, List

from app.core.config import settings


class LlmService:
    def generate(self, question: str, facts: List[Dict[str, Any]], sources: List[Dict[str, str]]) -> str:
        if not settings.llm_available:
            raise RuntimeError("LLM 未配置，请设置 qa_llm_api_url 环境变量")

        prompt = self._build_prompt(question, facts, sources)
        payload = {
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": settings.llm_max_tokens,
            "temperature": 0.3,
        }

        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            settings.llm_api_url,
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.llm_api_key}",
            },
        )

        with urllib.request.urlopen(request, timeout=settings.llm_timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
            return self._extract_answer(body)

    def _system_prompt(self) -> str:
        return (
            "你是一个专业的文物知识问答助手。你的回答必须基于用户提供的事实数据。\n"
            "规则：\n"
            "1. 优先基于给定的事实数据生成流畅、自然、有信息量的中文回答\n"
            "2. 不要编造事实数据中不存在的信息\n"
            "3. 在回答末尾不要添加'如果你还有其他问题'之类的客套话\n"
            "4. 回答简洁清晰，适合在对话界面展示\n"
            "5. 如果事实中包含了来源信息（博物馆名称等），可以在回答中自然地提及"
        )

    def _build_prompt(self, question: str, facts: List[Dict[str, Any]], sources: List[Dict[str, str]]) -> str:
        parts = [f"用户问题：{question}\n"]

        if facts:
            parts.append("知识图谱事实数据：")
            for i, fact in enumerate(facts, 1):
                subject = fact.get("subject", "")
                predicate = fact.get("predicate", "")
                object_val = fact.get("object", "")
                source = fact.get("source_name", "")
                if subject and predicate and object_val:
                    line = f"  {i}. {subject} 的 {predicate} = {object_val}"
                    if source:
                        line += f"（来源：{source}）"
                    parts.append(line)

        if sources:
            parts.append("\n参考来源：")
            for src in sources:
                name = src.get("source_name") or src.get("name", "")
                if name:
                    parts.append(f"  - {name}")

        parts.append("\n请基于以上事实数据生成自然流畅的回答：")
        return "\n".join(parts)

    def _extract_answer(self, body: Dict[str, Any]) -> str:
        choices = body.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content", "")
            if content:
                return content.strip()
        raise RuntimeError(f"LLM 返回数据格式异常: {json.dumps(body, ensure_ascii=False)[:200]}")
