from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "文物知识问答子系统"
    app_version: str = "0.1.0"
    default_mode: str = "rule"
    graph_backend: str = "hybrid"
    llm_backend: str = "mock"
    context_window: int = 5
    kg_api_base_url: str = "https://se-cs2305.yazs.top"
    kg_api_timeout_seconds: float = 10.0

    model_config = SettingsConfigDict(env_prefix="qa_", extra="ignore")


settings = Settings()