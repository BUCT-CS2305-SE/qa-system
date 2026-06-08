from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "文物知识问答子系统"
    app_version: str = "0.1.0"
    default_mode: str = "rule"

    # Data team's KG API
    graph_backend: str = "remote"
    kg_api_base_url: str = "https://se-cs2305.yazs.top"
    kg_api_timeout_seconds: float = 15.0
    kg_api_key: str = ""
    kg_api_key_header: str = "Authorization"
    kg_api_key_prefix: str = "Bearer "

    qa_query_enabled: bool = True

    # LLM (optional)
    llm_backend: str = "mock"
    llm_api_url: str = ""
    llm_api_key: str = ""
    llm_model: str = "gpt-3.5-turbo"
    llm_timeout_seconds: float = 30.0
    llm_max_tokens: int = 500

    context_window: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_prefix="qa_", extra="ignore")

    @property
    def llm_available(self) -> bool:
        return self.llm_backend != "mock" and bool(self.llm_api_url)


settings = Settings()
