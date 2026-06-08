# 文物知识问答子系统 — 模块与分工报告

---

## 一、系统模块总览

```
┌──────────────────────────────────────────────────────────────────┐
│                         qa-system                                │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  web-frontend │  │backend-spring│  │rag-service-  │           │
│  │  前端         │  │  后端网关     │  │  node        │           │
│  │  React 19    │  │  Spring Boot │  │  RAG 核心    │           │
│  │  :5173       │  │  :8081       │  │  FastAPI:8000│           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
│         │                 │                 │                   │
│  ┌──────┴─────────────────┴─────────────────┴───────┐           │
│  │              数据组 KG API                         │           │
│  │         https://se-cs2305.yazs.top                │           │
│  └───────────────────────────────────────────────────┘           │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  specs/  │  │  infra/  │  │ scripts/ │  │  docs/   │        │
│  │ API契约  │  │ Docker   │  │ 部署脚本  │  │ 设计文档  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 二、模块明细与功能清单

### 模块1：web-frontend（前端）

| 子模块 | 功能 | 文件 |
|--------|------|------|
| 问答对话界面 | ChatBox 消息展示（用户/助手气泡、头像、打字动画） | `ChatBox.tsx` |
| 问题输入 | ChatComposer 多行输入框，Enter 发送，Shift+Enter 换行 | `ChatComposer.tsx` |
| 顶部信息栏 | 标题、描述、Neo4j+RAG 技术标识 | `ChatHeader.tsx` |
| 侧边栏 | 会话列表（新建/删除/切换）、连接状态、反馈入口 | `SideHistory.tsx` |
| 会话管理 | localStorage 持久化、5天TTL、每小时GC、上限500条 | `useChat.ts` |
| API 客户端 | `POST /api/qa/ask` / `POST /api/qa/feedback` / 历史查询，超时控制、API Key鉴权 | `backendClient.ts` |
| 前端意图分类 | 正则硬匹配本地意图粗筛（图片搜索/尺寸/收藏地/材质/作者） | `qa.ts` |
| 答案溯源展示 | sources 列表（来源名+可点击链接）、facts 列表、LLM标注 | `ChatBox.tsx` |
| 反馈按钮 | 每条助手消息下方 👍/👎，发送至后端 | `ChatBox.tsx` |
| 样式系统 | 23个CSS变量、布局、动画、响应式 | `app.css` |

**负责人**：__________

---

### 模块2：backend-spring（后端网关）

| 子模块 | 功能 | 文件 |
|--------|------|------|
| 统一入口 | `POST /api/qa/ask` 代理转发至 RAG 服务，含重试+降级 | `QaController.java` + `QaServiceImpl.java` |
| 健康检查 | `GET /api/qa/health` | `QaController.java` |
| 反馈接口 | `POST /api/qa/feedback` 落库 + 转发 RAG | `QaController.java` |
| 历史查询 | `GET /api/qa/history/list` 按会话分页查询 | `HistoryController.java` + `HistoryServiceImpl.java` |
| API 鉴权 | `X-Api-Key` 头校验，health 免鉴权 | `ApiKeyFilter.java` |
| IP 限流 | 滑动窗口 60秒/60次，超限返回 429 | `RateLimitInterceptor.java` |
| CORS | 允许 localhost:5173 跨域 | `CorsConfig.java` |
| RAG 客户端 | RestTemplate 调 RAG 服务，指数退避重试 | `HttpRagClient.java` |
| 历史持久化 | H2 数据库存储问答记录（含 sources、facts JSON） | `HistoryEntity.java` + `HistoryRepository.java` |
| 历史清理 | 定时任务每日 03:10 清理 30 天前数据 | `HistoryCleanupJob.java` |
| 指标监控 | Micrometer 计数器（QPS、延迟、错误率） | `QaServiceImpl.java` |
| DTO 模型 | AskRequest / AskResponse / HistoryDto 字段映射 | `dto/` 目录 |
| 单元测试 | 6 个 QaService 测试 + 10 个 AskResponse 序列化测试 | `QaServiceTest.java` / `AskResponseTest.java` |
| 反馈存储 | 反馈记录 JPA 实体 + Repository | `FeedbackEntity.java` + `FeedbackRepository.java` |

**负责人**：__________

---

### 模块3：rag-service-node（RAG 核心）

#### 3.1 输入理解

| 功能 | 说明 | 文件 |
|------|------|------|
| 问题规范化 | trim 空格、统一标点、去语气词 | `normalizer.py` |
| 实体抽取 | 别名匹配（22条，4类：文物/博物馆/朝代/作者） | `entity_extractor.py` |
| 意图分类 | 关键词打分 + 实体加分，16 类意图 | `intent_classifier.py` |
| 上下文解析 | 代词指代消解、话题切换检测、30分钟超时 | `context_resolver.py` |
| 实体推理 | 无别名匹配时从问题文本提取候选实体名 | `service.py`（`_infer_missing_entities`） |

#### 3.2 查询构建

| 功能 | 说明 | 文件 |
|------|------|------|
| 意图→Cypher 模板 | 16 个 Neo4j Cypher 查询模板 | `templates.py` |
| 参数填充 | 从 UnderstandingResult 提取实体名填入模板参数 | `service.py` |
| 多实体支持 | compare_artifacts 场景支持传 artifact_names 列表 | `service.py` |

#### 3.3 KG 检索

| 功能 | 说明 | 文件 |
|------|------|------|
| 远程 API 调度 | 按模板名分派到数据组 8 个 API 端点 | `service.py`（`_retrieve_from_remote`） |
| 文物属性查询 | `/artifacts/{id}/property?prop=`（6种属性） | `service.py` |
| 相关推荐 | `/artifacts/{id}/related` | `service.py` |
| 作者生平 | `/qa/grounding/{id}` | `service.py` |
| 朝代代表 | `POST /qa/query` | `service.py` |
| 馆藏量统计 | `/stats/summary` | `service.py` |
| 多跳推理 | `/graph/neighbors/{id}?depth=2` | `service.py` |
| 文物对比 | `POST /artifacts/compare` | `service.py` |
| 分布统计 | `/stats/distribution` | `service.py` |
| 流转路径 | `/graph/neighbors/{id}?depth=2` | `service.py` |
| 降级兜底 | hybrid 模式 API 不通时自动切 mock | `service.py` |
| Mock 数据 | 16 个模板的完整假数据 | `mock_data.py` |

#### 3.4 答案生成

| 功能 | 说明 | 文件 |
|------|------|------|
| 规则模板 | 16 类意图的中文自然语言答案模板 | `service.py`（`_build_answer`） |
| LLM 润色 | 配置 DeepSeek/OpenAI 后自动调用 LLM 生成 | `llm/service.py` |
| 溯源组装 | sources + facts 去重合并 | `qa_pipeline.py` |

#### 3.5 管道编排

| 功能 | 说明 | 文件 |
|------|------|------|
| 主流程 | 串联 输入理解→查询构建→KG检索→答案生成→溯源→记录 | `qa_pipeline.py` |
| 错误处理 | unknown/clarify/no_data/exception 分级返回 | `qa_pipeline.py` |
| 反馈记录 | 内存日志 + 统计汇总（意图分布/状态分布/失败清单） | `qa_pipeline.py` + `logging_feedback/service.py` |

#### 3.6 配置

| 功能 | 说明 | 文件 |
|------|------|------|
| Pydantic Settings | 环境变量注入：graph_backend、LLM参数、超时、上下文窗口 | `core/config.py` |
| 意图规则 | 16 条意图定义的 JSON 配置 | `config/intent_rules.json` |
| 实体别名 | 22 条实体别名的 JSON 配置 | `config/entity_aliases.json` |

#### 3.7 Pydantic 模型

| 文件 | 内容 |
|------|------|
| `models/api.py` | QAAskRequest / QAAskResponse / FeedbackRequest / FeedbackResponse |
| `models/domain.py` | EntityMention / UnderstandingResult / QueryPlan / RetrievedFact / RetrievalResult / GeneratedAnswer |
| `models/errors.py` | 8 个错误码常量（2000~5004） |

#### 3.8 API 路由 + 单元测试

| 功能 | 说明 | 文件 |
|------|------|------|
| `/api/qa/ask` | 核心问答路由 | `api/routes/qa.py` |
| `/api/qa/feedback` | 反馈路由 | `api/routes/qa.py` |
| `/api/qa/summary` | 统计摘要 | `api/routes/qa.py` |
| `/api/health` | 健康检查 | `api/routes/health.py` |
| 单元测试 | 19 个测试用例（16意图 + 多轮 + 反馈 + 无数据） | `tests/test_pipeline.py` |

**负责人**：__________

---

### 模块4：specs / infra / scripts（工程化）

| 文件 | 功能 | 负责人 |
|------|------|--------|
| `specs/api-contract.md` | 4 个接口的完整契约文档（请求/响应/错误码/鉴权/限流） | __________ |
| `infra/docker-compose.yml` | 三服务编排（健康检查 + 依赖顺序） | __________ |
| `rag-service-node/Dockerfile` | Python RAG 服务镜像 | __________ |
| `backend-spring/Dockerfile` | Maven 多阶段构建 Spring Boot 镜像 | __________ |
| `web-frontend/Dockerfile` | Vite 构建 + Nginx 镜像 | __________ |
| `scripts/start-dev.ps1` | Windows 一键启动全栈 | __________ |
| `scripts/stop-dev.ps1` | Windows 停止所有服务 | __________ |
| `scripts/docker-deploy.ps1` | Docker Compose 一键部署 | __________ |
| `scripts/run-tests.ps1` | 回归测试 | __________ |

---

### 模块5：数据与配置

| 文件 | 功能 | 负责人 |
|------|------|--------|
| `data/samples/questions.json` | 33 条测试题集（覆盖 16 类意图） | __________ |
| `rag-service-node/openapi.json` | 数据组 KG API 参考文档 | 数据组提供 |
| `.env` | RAG 服务环境变量 | __________ |
| `web-frontend/.env` | 前端环境变量 | __________ |

---

## 三、分工填报表

| 角色 | 负责模块 | 姓名 |
|------|----------|------|
| **组长/集成** | 整体把控、env 合并、验收演示、文档汇总 | |
| **前端** | 模块1：web-frontend 全部 | |
| **后端** | 模块2：backend-spring 全部 | |
| **RAG 核心** | 模块3：rag-service-node 全部（输入理解、查询构建、KG检索、答案生成、编排） | |
| **工程化/测试** | 模块4：Docker、脚本、题集构建、测试、API契约 | |

> 注：每个模块的负责人对号填入最右列即可。
