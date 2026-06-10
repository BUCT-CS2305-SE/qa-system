# qa-system — 文物知识问答子系统

基于知识图谱（Neo4j）+ 大语言模型（LLM）的检索增强生成（RAG）问答系统，面向 Web 用户提供自然语言文物知识查询服务。

**项目状态：已完成交付** | 开发周期：2026-05-04 ~ 2026-06-10（第 9~15 周）

---

## 系统架构

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  web-frontend │────▶│backend-spring│────▶│rag-service-  │────▶│ 数据组 KG API │
│  React 19    │     │ Spring Boot  │     │    node       │     │ se-cs2305.   │
│  Vite 8      │     │ :8081        │     │ FastAPI :8000│     │ yazs.top     │
│  :5173       │     │ 鉴权/限流/转发│     │ RAG 管道      │     │ JWT 鉴权     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

RAG 管道流程：`问题 → 规范化 → 上下文解析 → 实体抽取 → 意图分类 → 查询构建 → KG 检索 → 答案生成 → 溯源`

---

## 快速开始

### 安装依赖

```powershell
# 前端
cd web-frontend; pnpm install

# Python RAG 服务
cd rag-service-node; python -m pip install -r requirements.txt

# Java 后端（需 Maven）
cd backend-spring; mvn clean package -DskipTests
```

### 一键启动

```powershell
.\scripts\start-dev.ps1
```

### 访问

| 服务 | 地址 |
|------|------|
| Web 前端 | http://localhost:5173 |
| 后端网关 | http://localhost:8081 |
| RAG 服务 | http://localhost:8000 |

### Docker 部署

```powershell
.\scripts\docker-deploy.ps1 -Action up
```

---

## 核心功能

| 功能 | 覆盖 | 状态 |
|------|------|:---:|
| 简单问答 | 12 类（收藏地/年代/材质/类型/介绍/作者/生平/同作者/同朝代/尺寸/推荐/馆藏量） | ✅ |
| 复杂问答 | 4 类（多跳推理/文物对比/朝代统计/流转路径） | ✅ |
| 多轮对话 | 代词指代 + 话题切换 + 30min 超时 + 前后端双存储 | ✅ |
| 无数据兜底 | KG 无数据时返回"暂无相关数据"，禁止编造 | ✅ |
| 答案溯源 | 每条回答含 `source_name` + `detail_url`，可点击跳转 | ✅ |
| 反馈机制 | 👍/👎 按钮 → 落库 → RAG 统计 | ✅ |
| 鉴权 | 双重鉴权（X-Api-Key + JWT 透传至 KG API） | ✅ |
| 限流 | IP 滑动窗口 60s/60 次 | ✅ |
| 中/英文搜索 | 自动检测语种，分别使用 lang=zh / lang=en | ✅ |
| 工程化 | Docker Compose 三服务 + 一键脚本 + CI | ✅ |

### 未完成（推迟至下阶段）

| 项目 | 说明 |
|------|------|
| 文档 RAG（向量检索） | 在 KG 之外增加文档语义检索通路 |
| LangChain 集成 | 用 LangChain 统一编排检索链 |

---

## 测试

```powershell
# 一键质量检查（lint + test）
.\scripts\quality.ps1

# 仅测试
.\scripts\run-tests.ps1                 # Python 单元 + 回归（55 用例）
cd rag-service-node; python -m pytest tests/test_integration.py -v  # 真实 KG 集成测试（33 用例）
cd web-frontend; pnpm test              # 前端 Vitest（3 用例）
cd backend-spring; mvn test             # Java JUnit
```

| 层级 | 用例数 | 通过率 |
|------|:------:|:------:|
| Python 单元 + 回归 | 55 | 100% |
| Python 集成（真实 KG） | 33 | 100% |
| 前端 Vitest | 3 | 100% |
| **合计** | **91** | **100%** |

---

## 目录结构

```
qa-system/
├── web-frontend/          React 19 + Vite 8 前端
│   ├── src/components/    ChatBox / ChatComposer / ChatHeader / SideHistory
│   ├── src/hooks/         useChat 会话管理
│   ├── src/api/           backendClient.ts  API 客户端
│   └── src/styles/        CSS 变量 + 暗色/亮色主题
├── backend-spring/        Spring Boot 3.1.4 网关
│   └── src/main/java/     鉴权/限流/转发/历史/反馈/监控
├── rag-service-node/      Python 3.13 + FastAPI RAG 核心
│   ├── app/services/      输入理解/查询构建/KG检索/答案生成/反馈
│   ├── app/models/        Pydantic 数据模型
│   ├── app/config/        意图规则/实体别名 JSON 配置
│   └── tests/             55 个自动化测试
├── infra/                 docker-compose.yml 三服务编排
├── scripts/               一键启动/停止/部署/测试/质量检查
├── specs/                 API 契约文档
└── docs/                  设计/技术栈文档
```

---

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/qa/ask` | POST | 核心问答（question + session_id → answer + sources + facts） |
| `/api/qa/feedback` | POST | 反馈记录（request_id + helpful + comment） |
| `/api/qa/history/list` | GET | 历史消息分页查询 |
| `/api/qa/health` | GET | 健康检查（免鉴权） |
| `/api/qa/summary` | GET | 问题统计摘要（RAG 服务） |

详细契约见 `specs/api-contract.md`。

---

## 文档索引

| 文档 | 路径 |
|------|------|
| 需求规格说明书 | `requirements_specification.md` |
| 设计报告 | `design_report.md` |
| 项目管理计划 | `project_management_plan.md` |
| 模块与分工报告 | `MODULE_REPORT.md` |
| 项目完成度总结 | `COMPLETION_SUMMARY.md` |
| 测试报告 | `TEST_REPORT.md` |
| 用户使用手册 | `USER_MANUAL.md` |
| API 契约 | `specs/api-contract.md` |
| 会议纪要（第 9~15 周） | `qa-system.wiki/` |

---

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React 19 · TypeScript · Vite 8 · Axios |
| 网关 | Spring Boot 3.1.4 · Java 17 · H2 · Micrometer |
| RAG | Python 3.13 · FastAPI · Pydantic |
| 知识图谱 | Neo4j（通过数据组 API 访问） |
| LLM | DeepSeek（可选配置） |
| 质量 | Vitest · ESLint · Ruff · pytest · Checkstyle · JaCoCo |
| 部署 | Docker Compose · Nginx · GitHub Actions CI |
