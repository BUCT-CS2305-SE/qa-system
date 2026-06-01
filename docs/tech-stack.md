# 中国图书馆 QA 子系统技术栈报告（草案）

日期：2026-05-10

## 1. 目标与范围

该 QA 子系统面向 Web 用户提供“问题 -> 答案 + 来源”的问答能力，数据形态包含：

- **知识图谱**：使用 Neo4j 存储实体/关系/属性，支持 Cypher 查询。
- **文本与文件**：先采用“解析为 text -> 分块 chunk -> 向量索引”的方式实现文档检索（RAG）。

约束：本阶段先完成工程结构与技术路线定义，不落业务代码。

## 2. 总体架构（建议）

采用“Spring 业务后端 + Node RAG 微服务 + TS Web 前端”的三层结构：

1) **backend-spring（Spring Boot）**
- 对外统一 API：`/api/qa/ask`
- 负责：
  - Neo4j 图谱查询（规则/模板 Cypher）
  - 问答编排：图谱 facts + 文档检索 chunks 聚合
  - 鉴权、审计日志、限流（可配合 Redis）
  - 调用 LLM（可由 Spring 直连模型网关，或转发给 Node）

2) **rag-service-node（Node.js + TypeScript）**
- 负责：
  - 文档解析后的 chunk 向量化（Embedding）
  - pgvector 召回、过滤、（可选）重排与 query extension
  - 统一返回文档证据：chunks + source 元信息
- 复用来源：优先从 FastGPT 的 `packages/service` 抽取或参考实现。

3) **web-frontend（TypeScript）**
- 负责：
  - Chat UI（问题输入、答案展示）
  - 来源（sources）列表与跳转展示
  - （可选）登录态与用户历史

## 3. 关键依赖与存储选型

### 3.1 知识图谱
- 数据库：Neo4j
- 查询语言：Cypher
- Spring 侧建议：Spring Data Neo4j 或 neo4j-java-driver 直连。

### 3.2 文档检索（RAG）
- 文档处理：
  - 第一阶段：文件/页面内容 **统一解析为纯文本**
  - 分块策略：按长度/段落/句子切 chunk（后续可升级）
- 向量化：Embedding 模型（与 FastGPT 兼容的调用方式）

### 3.3 向量库
- 数据库：PostgreSQL + pgvector
- 使用方式：
  - Mongo 负责存 chunk 文本与元数据
  - pgvector 负责存向量与与 chunkId 的映射

### 3.4 MongoDB
用途建议：
- chunk 元数据与原文（docId、chunkIndex、text、sourceUrl、更新时间等）
- 问答日志（question、intent、entities、cypher、sources、耗时等）
- 异步任务状态（导入、解析、建索引）

### 3.5 Redis
用途建议：
- 缓存：热门查询、统计计数
- 限流：接口频控
- 分布式锁：避免重复建索引/重复训练

## 4. LLM 与输出规范

### 4.1 输出结构（建议）
- `answer: string`
- `sources: Array<{ type: 'neo4j' | 'doc', title: string, url: string, evidence?: string, score?: number }>`
- `debug?: { intent?: string, entities?: any, cypher?: string, ragQuery?: string, elapsedMs?: number }`

### 4.2 真实性约束
- 图谱/文档均未命中时：必须返回固定提示（例如“暂无相关数据”），禁止臆造。
- 所有回答需携带可点击的来源链接（至少 1 个或明确标注无来源）。

## 5. 与 FastGPT 的复用边界

- 可复用（或参考）能力：
  - embedding、query extension、向量召回与检索流程（`packages/service` 内相关实现）
  - sources/quote 的组织思路（用于统一返回结构）
- 需要自建：
  - Neo4j 数据模型与 Cypher 查询服务层
  - Spring 的对外 API 与权限体系（按项目要求落地）

## 6. 推荐里程碑（高层）

1) 最小闭环：
- 文档 text -> chunk 入库 -> pgvector 建索引 -> 可召回 sources
- Neo4j 规则问答（至少 10 类）
- Web 页面可问答并展示来源

2) 核心增强：
- query extension、重排、缓存
- 文档类型扩展（PDF/HTML 等）
- 统一观测：日志、指标、追踪

## 7. FastGPT 可复用模块清单（路径级）

> 说明：本清单用于后续从 FastGPT 仓库抽取或参考实现。是否“直接复制代码”取决于你们最终的工程拆分方式（推荐抽成独立 `rag-service-node` 微服务）。

### 7.1 Query Extension（问句扩写/改写）
- `packages/service/core/ai/functions/queryExtension.ts`
- `packages/service/core/workflow/dispatch/tools/queryExternsion.ts`（工作流节点封装，可选参考）

### 7.2 Embedding（文本向量化）
- `packages/service/core/ai/embedding/index.ts`

### 7.3 向量存储与召回（pgvector 为主，Redis 做缓存）
- `packages/service/common/vectorDB/controller.ts`
- `packages/service/common/vectorDB/controller.d.ts`
- `packages/service/common/vectorDB/pg/**`（pgvector 具体实现；目录名以实际仓库为准）
- `packages/service/common/redis/cache`（向量计数 cache 等能力在该处依赖）

### 7.4 检索（RAG）流程（可选抽取为你们的“文档检索服务”核心）
- `packages/service/core/dataset/search/controller.ts`
- `packages/service/core/dataset/search/utils.ts`
- `packages/service/core/workflow/dispatch/dataset/search.ts`（工作流调度式检索，可选）

### 7.5 对话/日志（如你们需要保存问答历史，可参考其 schema/字段）
- `packages/service/core/chat/controller.ts`
- `packages/service/core/chat/chatSchema.ts`

## 8. 前端页面与接口对齐说明

- 前端占位页面放在：`china-library-qa/web-frontend/index.html`
- 当前为离线 mock：不请求接口、仅展示 answer + sources + debug 的 UI 结构
- 后续接入时：
  1) 将页面中 `send()` 的 mock 逻辑替换为 `fetch('/api/qa/ask', ...)`
  2) 把返回的 `answer/sources/debug` 用同样的渲染逻辑展示即可
