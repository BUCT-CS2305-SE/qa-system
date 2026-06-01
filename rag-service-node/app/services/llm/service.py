from __future__ import annotations

import json
import urllib.request
from typing import Any, Dict, List

from app.core.config import settings


class LlmService:
    def generate(self, question: str, facts: List[Dict[str, Any]], sources: List[Dict[str, str]]) -> str:
        if not settings.llm_available:
            raise RuntimeError("LLM 未配置")

        prompt = self._build_qa_prompt(question, facts, sources)
        return self._call_llm(prompt)

    def chat(self, question: str, history: List[Dict[str, str]] | None = None) -> str:
        if not settings.llm_available:
            raise RuntimeError("LLM 未配置")

        messages = [{"role": "system", "content": self._chat_system_prompt()}]
        if history:
            for entry in history[-10:]:
                role = entry.get("role", "user")
                content = entry.get("text", "")
                if content:
                    messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": question})

        payload = {
            "model": settings.llm_model,
            "messages": messages,
            "max_tokens": settings.llm_max_tokens,
            "temperature": 0.5,
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            settings.llm_api_url, data=data, method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.llm_api_key}",
            },
        )
        with urllib.request.urlopen(request, timeout=settings.llm_timeout_seconds) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return self._extract_answer(body)

    # ── QA prompt (structured facts → polished answer) ─────────

    def _build_qa_prompt(self, question: str, facts: List[Dict[str, Any]], sources: List[Dict[str, str]]) -> str:
        parts = [f"用户问题：{question}\n"]
        if facts:
            parts.append("知识图谱事实数据：")
            for i, fact in enumerate(facts, 1):
                s, p, o = fact.get("subject", ""), fact.get("predicate", ""), fact.get("object", "")
                src = fact.get("source_name", "")
                if s and p and o:
                    line = f"  {i}. {s} 的 {p} = {o}"
                    if src:
                        line += f"（来源：{src}）"
                    parts.append(line)
        if sources:
            parts.append("\n参考来源：")
            for src in sources:
                name = src.get("source_name") or src.get("name", "")
                if name:
                    parts.append(f"  - {name}")
        parts.append("\n请基于以上事实数据生成自然流畅的回答：")
        return "\n".join(parts)

    def _call_llm(self, prompt: str) -> str:
        payload = {
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": self._qa_system_prompt()},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": settings.llm_max_tokens,
            "temperature": 0.3,
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            settings.llm_api_url, data=data, method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.llm_api_key}",
            },
        )
        with urllib.request.urlopen(request, timeout=settings.llm_timeout_seconds) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return self._extract_answer(body)

    # ── Prompts ────────────────────────────────────────────────

    def _qa_system_prompt(self) -> str:
        return (
            "你是一个专业的文物知识问答助手。你的回答必须基于用户提供的事实数据。\n"
            "规则：\n"
            "1. 优先基于给定的事实数据生成流畅、自然、有信息量的中文回答\n"
            "2. 不要编造事实数据中不存在的信息\n"
            "3. 在回答末尾不要添加'如果你还有其他问题'之类的客套话\n"
            "4. 回答简洁清晰，适合在对话界面展示\n"
            "5. 如果事实中包含了来源信息（博物馆名称等），可以在回答中自然地提及"
        )

    def _chat_system_prompt(self) -> str:
        return (
            "你是一个专业的文物知识问答与文化导览助手，名为'文物助手'。\n"
            "你的知识领域是中国海外流失文物，包括文物信息、博物馆、朝代、材质、作者等。\n\n"
            "对话规则：\n"
            "1. 优先基于你的文物知识回答用户问题，回答要流畅自然\n"
            "2. 如果用户问的问题超出文物/博物馆/历史/艺术领域，礼貌地说明你的知识范围并引导回文物话题\n"
            "3. 支持多轮对话，能理解上下文中的指代（如'它'、'这件'、'那个博物馆'）\n"
            "4. 回答简洁清晰，适合在对话界面展示，一般不超过200字\n"
            "5. 不要编造具体的文物数据，如果不确定就说需要查询知识图谱\n"
            "6. 可以推荐相关文物、朝代或博物馆供用户进一步了解"
        )

    # ── Utility ────────────────────────────────────────────────

    def _extract_answer(self, body: Dict[str, Any]) -> str:
        choices = body.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content", "")
            if content:
                return content.strip()
        raise RuntimeError(f"LLM 返回数据格式异常: {json.dumps(body, ensure_ascii=False)[:200]}")
