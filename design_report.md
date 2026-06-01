# 问答子系统（qa-system）设计报告

版本：v0.1

## 1. 概述

本设计报告描述“文物知识问答子系统”的总体架构、关键模块设计、接口约定与演进路线。系统采用“知识图谱（Neo4j）+（可选）文档检索 + 大语言模型”的检索增强生成（RAG）思路：

- **事实准确性优先**：答案核心事实来自知识图谱检索结果（facts）。
- **语言表达增强（可选）**：在有充分证据的前提下，LLM 对 facts/chunks 进行自然语言组织与补充说明。
- **强制无数据兜底**：无法得到支撑事实时返回“暂无相关数据”，禁止编造。
- **溯源展示**：每条回答必须带来源（source_name + detail_url/source_url）。

## 2. 设计目标与约束

### 2.1 设计目标

- 支持至少 10 类简单问答（属性查询/列表查询/推荐类）。
- 输出结构稳定，前端可直接渲染。
- 具备可观测性（request_id、耗时、命中情况、失败原因）。
- 支持后续演进：多轮对话、复杂推理、文档 RAG、LangChain 链路工程化。

### 2.2 关键约束

- **no_data**：KG/检索证据不足 → 必须 no_data=true + “暂无相关数据”。
- **事实/生成区分**：LLM 补充内容与 KG facts 必须可区分。
- **可回归**：维护最小题集与单测，保证迭代不回退。

## 3. 总体架构

### 3.1 组件视图

- `web-frontend/`（React + TS + Vite）
  - 输入问题、展示对话
  - 展示 sources 与（可选）facts
  - 反馈入口（选做）

- `backend-spring/`（Spring Boot，聚合/治理层）
  - 对外统一入口：`POST /api/qa/ask`
  - 鉴权/限流/日志/错误码
  - 调用 RAG 服务并做兜底与治理（重试/熔断可选）

- `rag-service-node/`（当前 Python + FastAPI 原型服务）
  - 输入理解、查询构建、KG 检索、答案组织、溯源、反馈记录
  - 逐步：mock → Neo4j → 文档 RAG/LLM

- 存储/基础设施（按阶段引入）
  - Neo4j（KG）
  - Redis（缓存/上下文/限流，可选）
  - pgvector/Milvus（文档向量检索，可选）

### 3.2 数据流（核心链路）

1) 用户在前端输入 question
2) 前端调用 `/api/qa/ask`
3) 后端将请求转发/编排给 `rag-service-node`
4) RAG 服务：意图识别/实体抽取 → 生成 Cypher → KG 检索 facts
5) 生成 answer：
   - 规则/模板输出（阶段 A/B）
   - 或 LangChain/LLM 生成（阶段 C，需 evidence 约束）
6) 返回 answer + sources (+ facts)

## 4. 关键模块设计（rag-service-node）

> 当前原型已经具备模块分层，可作为正式实现的骨架。

### 4.1 输入理解（Input Understanding）

- **标准化**：清洗空格/标点、简繁/大小写统一等（按需要）。
- **实体抽取**：从问题中提取文物名、作者名、朝代、博物馆等。
- **意图识别**：将问题映射到预定义意图标签（至少覆盖 10 类）。
- **上下文消歧（选做）**：多轮场景下进行代词指代与实体延续。

**产出**：
- `intent`（意图标签）
- `entities`（归一后的实体字典）
- `confidence`（可选）

### 4.2 查询构建（Query Builder）

- 为每类意图维护一套 **Cypher 模板**
- 将 `entities` 映射到模板参数
- 输出：
  - `cypher`、`params`

### 4.3 KG 检索（KG Retrieval）

- 阶段 A：mock 数据（保证接口/链路可跑）
- 阶段 B：替换为 Neo4j 实查（Cypher）

输出：
- `facts`（结构化字段列表）
- `sources`（来源名与详情 URL）

### 4.4 答案组织与生成（Answer Generation）

- **规则/模板优先**：简单问答可直接由 facts 生成可控回答。
- **LLM 生成（选做）**：
  - 仅使用检索到的 facts/chunks 作为上下文
  - 强制结构化输出（JSON schema / output parser）
  - 不足证据 → no_data

### 4.5 溯源与可信度展示

- `sources` 必含：
  - `source_name`
  - `detail_url`（或统一命名 `source_url`，在 specs 固化）
- 可在前端将 facts 与模型补充描述分区显示。

### 4.6 反馈记录（Feedback，选做）

- `POST /api/qa/feedback`
- 记录：request_id、helpful、comment、原问题、意图、实体、命中情况

## 5. LangChain 设计落点（阶段 C）

LangChain 用于将检索与生成链路工程化：

- Retriever：
  - KG facts（结构化）
  - 文档 chunks（向量召回）
- Prompt：
  - 约束“只能基于证据回答”
  - 明确 no_data 规则
- Output Parser：
  - 强制输出 `answer/no_data/sources/facts` 结构
- Tools（选做）：
  - 将 Cypher 查询封装为受控工具（需要审计与白名单模板）

## 6. 接口设计（概要）

### 6.1 POST /api/qa/ask

- 请求：`question`，`session_id`（选做）
- 响应：`request_id`、`answer`、`no_data`、`sources[]`、`facts[]`

### 6.2 POST /api/qa/feedback（选做）

- 请求：`request_id`、`helpful`、`comment?`
- 响应：`ok`

### 6.3 GET /api/health

- 响应：`status`

## 7. 关键数据结构（建议）

### 7.1 Answer（建议）

- `answer: string`
- `no_data: boolean`
- `facts: Array<{ key: string; value: string; evidence?: string }>`
- `sources: Array<{ source_name: string; detail_url: string }>`

## 8. 安全与性能设计

- 鉴权与限流：由 `backend-spring` 统一承载（可接 Redis）。
- 超时与降级：下游 Neo4j/LLM/向量库不可用时返回可读错误，或降级为仅 KG/仅模板。
- 日志与追踪：全链路 request_id；记录意图、实体、查询耗时与命中情况。

## 9. 测试与验收设计

- 单元测试：输入理解/查询构建/答案组织
- 回归题集：≥30 条覆盖 10 类；记录通过率与失败原因
- 演示脚本：覆盖“命中/不命中/溯源/（可选）反馈”

## 10. 演进路线

- 阶段 A：FastAPI 原型 + mock 检索 + 规则回答
- 阶段 B：接入 Neo4j 实查（Cypher）+ 别名归一/消歧
- 阶段 C：接入文档向量检索 + LangChain/LLM 生成（结构化输出 + 强约束）
- 阶段 D（选做）：多轮对话、复杂问答、反馈闭环与质量看板
