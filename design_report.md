# 问答子系统（qa-system）设计报告

版本：v1.2（结项） | 更新日期：2026-06-10

---

## 1. 概述

本设计报告描述"文物知识问答子系统"的总体架构、关键模块设计、接口约定与实现细节。系统采用"知识图谱（Neo4j）+（可选）大语言模型"的检索增强生成（RAG）思路：

- **事实准确性优先**：答案核心事实来自知识图谱检索结果（facts），通过数据组 KG API 实时查询。
- **语言表达增强**：rule 模式使用 16 类中文模板直接生成回答；auto 模式调用 DeepSeek LLM 对 facts 进行自然语言润色。
- **强制无数据兜底**：无法得到支撑事实时返回"暂无相关数据"，hybrid 模式下真实 KG API 返回空结果时不降级到 mock。
- **溯源展示**：每条回答必须带来源（source_name + detail_url），前端可点击跳转。

---

## 2. 设计目标与约束

### 2.1 设计目标

| 目标 | 实际达成 |
|------|----------|
| 支持至少 10 类简单问答 | **16 类**（12 简单 + 4 复杂） |
| 输出结构稳定，前端可直接渲染 | `status/answer/sources/facts/no_data` 统一结构 |
| 具备可观测性（request_id、耗时、命中情况） | 全链路 request_id + Micrometer 指标 |
| 支持多轮对话、复杂推理 | 已完成（代词消解/话题切换/多跳/对比/统计/路径） |
| Docker 一键部署 | `docker-compose.yml` 三服务编排 |

### 2.2 关键约束

- **no_data**：KG/检索证据不足 → 必须 `no_data=true` + "暂无相关数据"，禁止编造
- **事实/生成区分**：LLM 润色内容标注 `💡 本回答由 deepseek-chat 基于知识图谱事实生成`，规则回答标注 `规则版`
- **可回归**：维护 33 条测试题集 + 55 个自动化用例，`run-tests.ps1` 一键回归

---

## 3. 总体架构

### 3.1 组件视图

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  web-frontend │────▶│backend-spring│────▶│rag-service-  │────▶│  数据组 KG    │
│  React 19    │     │ Spring Boot  │     │    node       │     │  API         │
│  Vite 8       │     │ :8081        │     │ FastAPI :8000│     │ se-cs2305.   │
│  :5173       │     │              │     │              │     │ yazs.top     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
      │                      │                     │
      │  Chat UI             │  鉴权/限流/转发      │  意图识别/实体抽取
      │  侧边栏/会话管理       │  历史记录(H2)        │  KG检索/答案生成
      │  来源展示/反馈按钮     │  反馈落库            │  溯源/日志
      │  暗色/亮色模式         │  CORS               │  中/英文自适应
      └──────────────────────┴─────────────────────┘
```

### 3.2 三服务详解

#### 3.2.1 web-frontend（React 19 + TypeScript + Vite 8）

| 组件 | 文件 | 功能 |
|------|------|------|
| ChatBox | `ChatBox.tsx` | 消息展示（用户/助手气泡、头像、打字动画）、sources 可点击链接、facts 列表、LLM/规则标注、反馈按钮 |
| ChatComposer | `ChatComposer.tsx` | 多行输入（Enter 发送 / Shift+Enter 换行）、自动聚焦 |
| ChatHeader | `ChatHeader.tsx` | 标题、描述、Neo4j+RAG 技术标识 |
| SideHistory | `SideHistory.tsx` | 会话列表（新建/删除/切换）、连接状态指示、反馈入口 |
| useChat | `useChat.ts` | 会话管理核心：localStorage 持久化（5 天 TTL + 每小时 GC + 500 条上限）、消息流 |
| backendClient | `backendClient.ts` | API 客户端：`/ask`、`/feedback`、`/history`，超时控制（30s）、API Key 鉴权、JWT token 透传 |
| 样式系统 | `app.css` | 23 个 CSS 变量、暗色/亮色兼容、响应式布局 |

#### 3.2.2 backend-spring（Spring Boot 3.1.4 + Java 17）

| 模块 | 文件 | 功能 |
|------|------|------|
| 统一入口 + 健康检查 | `QaController.java` | `POST /api/qa/ask`（代理转发至 RAG）、`GET /api/qa/health`（免鉴权） |
| 反馈接口 | `QaController.java` | `POST /api/qa/feedback` 落库 + 转发 RAG |
| 历史查询 | `HistoryController.java` | `GET /api/qa/history/list` 按会话分页查询 |
| API 鉴权 | `ApiKeyFilter.java` | `X-Api-Key` 头校验，health 免鉴权，401 拦截 |
| IP 限流 | `RateLimitFilter.java` | 滑动窗口 60s/60 次，超限 429 |
| CORS 配置 | `CorsConfig.java` | 允许 localhost:5173 + 局域网 IP 跨域 |
| RAG 客户端 | `HttpRagClient.java` | RestTemplate 调 RAG 服务，指数退避重试，JWT token 透传 |
| 历史持久化 | `HistoryEntity.java` + `HistoryRepository.java` | H2 存储问答记录（含 sources、facts JSON） |
| 历史清理 | `HistoryCleanupJob.java` | 定时任务每日 03:10 清理 30 天前数据 |
| 反馈存储 | `FeedbackEntity.java` + `FeedbackRepository.java` | 反馈记录 JPA 落库 |
| 指标监控 | `QaServiceImpl.java` | Micrometer 计数器（QPS、延迟、错误率） |

#### 3.2.3 rag-service-node（Python 3.13 + FastAPI）

| 子模块 | 文件 | 功能 |
|--------|------|------|
| 问题规范化 | `normalizer.py` | trim 空格、统一标点、去语气词 |
| 实体抽取 | `entity_extractor.py` | 别名匹配（22 条，4 类：文物/博物馆/朝代/作者），中/英文双语 |
| 意图分类 | `intent_classifier.py` | 关键词打分 + 实体加分，16 类意图，含裸实体名回退逻辑 |
| 上下文解析 | `context_resolver.py` | 代词指代消解（"它的材质"）、话题切换检测（信号词+意图变化+实体不相关）、30 分钟超时 |
| 查询构建 | `templates.py` | 意图 → 16 个模板映射，参数填充 |
| KG 检索 | `service.py` | 8 个数据组 API 端点调度，hybrid 双模（API 优先 + mock 降级），JWT 鉴权 |
| mock 数据 | `mock_data.py` | 16 个模板的完整假数据，含参数过滤 |
| 答案生成 | `service.py`（`_build_answer`） | 16 类中文规则模板；LLM 润色（DeepSeek/OpenAI 可配置） |
| 管道编排 | `qa_pipeline.py` | 主流程串联：输入理解 → 查询构建 → KG 检索 → 答案生成 → 溯源 → 记录 |
| 反馈记录 | `qa_pipeline.py` + `logging_feedback/` | 内存日志 + 统计汇总（意图分布/状态分布/失败清单） |
| 配置 | `core/config.py` | Pydantic Settings 环境变量注入：graph_backend、LLM 参数、超时、上下文窗口 |
| 意图规则 | `config/intent_rules.json` | 16 条意图定义 |
| 实体别名 | `config/entity_aliases.json` | 22 条实体别名的中/英文映射 |

---

## 4. 核心数据流（RAG 管道）

```
用户问题
  │
  ▼
┌─────────────┐
│  1. 规范化   │  trim、去语气词、语言检测（中/英）
└──────┬──────┘
       ▼
┌─────────────┐
│  2. 上下文   │  多轮：代词指代消解 / 话题切换检测 / 30min 超时清理
│     解析     │
└──────┬──────┘
       ▼
┌─────────────┐
│  3. 实体抽取  │  别名匹配（22 条，4 类）+ 问题文本推断（兜底）
└──────┬──────┘
       ▼
┌─────────────┐
│  4. 意图分类  │  关键词打分（16 规则）+ 实体加分 + 裸实体名回退
└──────┬──────┘
       ▼
┌─────────────┐
│  5. 查询构建  │  意图 → 模板映射（16 个）→ 参数填充
└──────┬──────┘
       ▼
┌─────────────┐
│  6. KG 检索  │  hybrid: 真实 KG API（8 端点）→ 失败降级 mock
│              │  remote: 仅真实 API，失败报错
│              │  mock: 仅 mock（开发/测试用）
└──────┬──────┘
       ▼
┌─────────────┐
│  7. 答案生成  │  rule: 16 类中文模板直接生成（~20ms）
│              │  auto: facts → LLM 润色 → 结构化输出（~3.5s）
└──────┬──────┘
       ▼
┌─────────────┐
│  8. 溯源组装  │  sources/facts 去重 + detail_url 附加
└──────┬──────┘
       ▼
┌─────────────┐
│  9. 记录     │  会话历史 + 反馈日志 + 指标计数
└──────┬──────┘
       ▼
    返回前端
```

### 4.1 16 类意图与对应的 KG API 端点

| 序号 | 意图标签 | 类型 | 数据组 API |
|------|----------|------|------------|
| 1 | `artifact_museum` | 简单 | `GET /artifacts/{id}/property?prop=museum_name` |
| 2 | `artifact_period` | 简单 | `GET /artifacts/{id}/property?prop=period` |
| 3 | `artifact_material` | 简单 | `GET /artifacts/{id}/property?prop=material` |
| 4 | `artifact_type` | 简单 | `GET /artifacts/{id}/property?prop=type` |
| 5 | `artifact_description` | 简单 | `GET /artifacts/{id}`（拼装多字段） |
| 6 | `artifact_dimensions` | 简单 | `GET /artifacts/{id}/property?prop=dimensions` |
| 7 | `painting_author` | 简单 | `GET /artifacts/{id}/property?prop=author` |
| 8 | `artist_biography` | 简单 | `GET /qa/grounding/{id}` → `GET /artifacts/{id}` |
| 9 | `same_artist_works` | 简单 | `GET /artifacts/{id}/related` |
| 10 | `dynasty_representative` | 简单 | `POST /qa/query` |
| 11 | `recommended_artifacts` | 简单 | `GET /artifacts/{id}/related` |
| 12 | `museum_count` | 简单 | `GET /stats/summary` |
| 13 | `multi_hop` | 复杂 | `GET /graph/neighbors/{id}?depth=2` |
| 14 | `compare_artifacts` | 复杂 | `POST /artifacts/compare` |
| 15 | `artifact_statistics` | 复杂 | `GET /stats/distribution` |
| 16 | `path_query` | 复杂 | `GET /graph/neighbors/{id}?depth=2` |

---

## 5. 接口设计

详细契约见 `specs/api-contract.md`，此处为设计概要。

### 5.1 POST /api/qa/ask

**请求**：
```json
{
  "question": "女史箴图在哪个博物馆？",
  "session_id": "uuid-xxx"
}
```

**响应**：
```json
{
  "request_id": "req-uuid",
  "answer": "女史箴图现藏于大英博物馆。",
  "no_data": false,
  "status": "ok",
  "intent": "artifact_museum",
  "sources": [
    { "source_name": "大英博物馆", "detail_url": "https://..." }
  ],
  "facts": [
    { "subject": "女史箴图", "predicate": "收藏地", "object": "大英博物馆" }
  ],
  "mode": "rule"
}
```

**状态码**：
| status | 含义 |
|--------|------|
| `ok` | 正常回答 |
| `no_data` | 证据不足，"暂无相关数据" |
| `clarify` | 需要用户澄清 |
| `unknown` | 无法识别意图 |
| `exception` | 系统错误 |

### 5.2 POST /api/qa/feedback

```json
{ "request_id": "req-uuid", "helpful": true, "comment": "回答很准确" }
```

### 5.3 GET /api/qa/history/list?session_id=xxx&page=1&size=20

返回该会话的历史消息分页列表。

### 5.4 GET /api/health

```json
{ "status": "ok" }
```

---

## 6. 安全设计

### 6.1 双重鉴权

```
前端 localStorage.auth_token
  → 后端提取 Authorization header
  → 注入 X-Kg-Token 转发 RAG
  → RAG 以 Authorization: Bearer <token> 调用 KG API
```

| 层级 | 机制 | 配置 |
|------|------|------|
| 前端 → 后端 | `X-Api-Key` header（`qa-demo-key`） | `ApiKeyFilter.java` |
| 前端 → 后端 | `Authorization` header（JWT） | 透传至 RAG |
| 后端 → RAG | `X-Kg-Token` header | `HttpRagClient.java` |
| RAG → KG API | `Authorization: Bearer <JWT>` | `qa_kg_api_key` 环境变量 |

### 6.2 IP 限流

- 算法：滑动窗口
- 窗口：60 秒
- 上限：60 次
- 超限响应：HTTP 429 + `{ "error": "请求过于频繁，请稍后再试" }`
- 实现：`RateLimitFilter.java`（Filter 级别），`ConcurrentHashMap<IP, Deque<timestamp>>`

---

## 7. 会话与多轮对话设计

### 7.1 三层存储

| 层 | 位置 | 策略 |
|----|------|------|
| 前端 | `localStorage` | 5 天 TTL，每小时 GC 过期会话，单会话上限 500 条 |
| 后端 | H2 数据库 | 持久化存储，每日 03:10 清理 30 天前数据 |
| RAG | 内存 `context_resolver` | 30 分钟无活动自动过期，轮次 + 时间双重裁剪 |

### 7.2 代词指代消解

```
规则匹配："它的材质" / "它的尺寸" / "他的生平" ...
  → 回查上一轮 assistant 回答中的实体
  → 继承实体，重新执行问答管道
```

### 7.3 话题切换检测

三重判断：
1. 信号词："换个话题"、"换一个"
2. 意图变化：新问题意图 != 上一轮意图
3. 实体不相关：新问题实体 != 缓存的上一轮实体

满足任一条件 → 清除缓存实体，开始新话题。

---

## 8. 部署架构

### 8.1 Docker Compose 编排

```yaml
services:
  rag:
    build: rag-service-node/
    ports: ["8000:8000"]
    healthcheck: curl localhost:8000/api/health

  backend:
    build: backend-spring/
    ports: ["8081:8081"]
    depends_on:
      rag: { condition: service_healthy }

  frontend:
    build: web-frontend/
    ports: ["5173:80"]
    depends_on:
      backend: { condition: service_healthy }
```

### 8.2 一键脚本

| 脚本 | 用途 |
|------|------|
| `scripts/start-dev.ps1` | 一键启动三服务（Python + Java + Vite） |
| `scripts/stop-dev.ps1` | 停止所有后台 Job |
| `scripts/docker-deploy.ps1` | Docker Compose 构建/启动/停止 |
| `scripts/run-tests.ps1` | 运行 pytest 55 用例 + 输出结论 |

---

## 9. 测试设计

### 9.1 测试分层

| 层级 | 工具 | 数量 | 覆盖 |
|------|------|------|------|
| 单元测试 | pytest | 19 个 | 16 意图 + 多轮上下文 + 反馈 + no_data |
| 回归题集 | pytest 参数化 | 36 个 | `questions.json` 全部 33 条 + 多轮场景 3 条 |
| 集成测试 | pytest + 真实 KG | 33 个 | 真实 KG API 全链路，含 LLM 模式 |
| HTTP 集成 | curl / Postman | 手动 | 鉴权/限流/健康检查边界 |

### 9.2 测试题集设计

`data/samples/questions.json`：33 条，覆盖 16 类意图，每条含 `question`、`expected_intent`、`expected_status`。
用作回归基准，每次变更后 `run-tests.ps1` 验证不退化。

---

## 10. 中/英文自适应设计

- 输入规范化时通过字符集检测判断语种
- 中文 → KG API 请求 `lang=zh`
- 英文 → KG API 请求 `lang=en`
- `entity_aliases.json` 同时维护中文名 → 英文名映射（如 "女史箴图" → "Admonitions Scroll"）
- 效果：英文文物名搜索精度显著提升

---

## 11. 演进路线回顾

| 阶段 | 计划 | 实际 |
|------|------|------|
| 阶段 A | FastAPI 原型 + mock + 规则回答 | ✅ 第 10 周完成 |
| 阶段 B | 接入真实 KG API + 别名归一/消歧 | ✅ 第 11~12 周完成 |
| 阶段 C | 多轮对话、复杂问答、反馈闭环 | ✅ 第 12~13 周完成 |
| 阶段 D | 文档 RAG + LangChain + 性能测试 | ⏳ 推迟至下一阶段 |
