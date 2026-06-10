from fastapi import FastAPI

from app.api.routes import health, qa
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于知识图谱与大语言模型的文物知识问答子系统框架",
)

app.include_router(health.router, prefix="/api")
app.include_router(qa.router, prefix="/api")
