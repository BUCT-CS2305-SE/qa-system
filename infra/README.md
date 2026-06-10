# 基础设施配置

| 文件 | 用途 |
|------|------|
| `docker-compose.yml` | 三服务编排（rag :8000 / backend :8081 / frontend :80），含健康检查依赖顺序 |

### Docker 镜像

| 服务 | Dockerfile 位置 | 技术栈 |
|------|----------------|--------|
| rag | `rag-service-node/Dockerfile` | Python 3.13 + FastAPI |
| backend | `backend-spring/Dockerfile` | Maven 多阶段构建 + JRE 17 |
| frontend | `web-frontend/Dockerfile` | Vite 构建 + Nginx |

### 一键部署

```powershell
.\scripts\docker-deploy.ps1 -Action build  # 构建镜像
.\scripts\docker-deploy.ps1 -Action up     # 启动
.\scripts\docker-deploy.ps1 -Action down   # 停止
```
