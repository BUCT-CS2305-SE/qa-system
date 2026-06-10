# 部署与操作脚本

| 脚本 | 用途 | 平台 |
|------|------|:---:|
| `start-dev.ps1` | 一键启动全栈开发环境（RAG :8000 + Spring Boot :8081 + Vite :5173） | Windows |
| `start-dev.sh` | 同上 | Linux/Mac |
| `stop-dev.ps1` | 停止所有后台开发服务 | Windows |
| `docker-deploy.ps1` | Docker Compose 构建/启动/停止（build / up / down） | Windows |
| `run-tests.ps1` | 运行 RAG 服务回归测试（55 用例 + 结果摘要） | Windows |
| `quality.ps1` | 一键代码质量检查（lint + test，支持 -Fast/-Frontend/-Backend/-Python） | Windows |
