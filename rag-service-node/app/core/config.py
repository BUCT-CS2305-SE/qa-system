from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "文物知识问答子系统"
    app_version: str = "0.1.0"
    default_mode: str = "rule"
    graph_backend: str = "mock"
    llm_backend: str = "mock"
    context_window: int = 5

    model_config = SettingsConfigDict(env_prefix="qa_", extra="ignore")


settings = Settings()