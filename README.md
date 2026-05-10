# qa-system
Implements intelligent question answering functionality based on the knowledge graph, supporting natural language queries and semantic matching.

# 中国图书馆 QA 子系统（规划与占位）

## 1. 子系统目标

面向 Web 用户提供“问题 -> 答案 + 来源（sources）”的问答能力，数据来源包括：

- **知识图谱（Neo4j）**：实体/关系/属性，使用 Cypher 查询事实（facts）。
- **文本/文件（RAG）**：先将文档解析为 text，分块（chunk）后做向量检索（pgvector），返回证据片段与来源链接。

输出要求：
- 查不到必须明确返回“暂无相关数据”，禁止臆造。
- 回答需携带可点击来源（至少一个或明确标注无来源）。

## 2. 总体架构（落地路线）

- `backend-spring/`（Spring Boot）：
  - 对外统一 QA API（建议：`POST /api/qa/ask`）
  - Neo4j 查询与规则问答（至少 10 类）
  - 聚合：图谱 facts + 文档 RAG chunks -> LLM 生成 -> answer + sources
  - 日志、鉴权、限流（可配合 Redis）

- `rag-service-node/`（Node.js + TS 微服务）：
  - 复用/参考 FastGPT 的 embedding、query extension、向量召回与检索流程
  - 存储：Mongo（chunk 与元数据）+ PostgreSQL(pgvector)（向量）+ Redis（缓存/锁/限流）

- `web-frontend/`（TypeScript + Vite）：
  - Web 问答页面（chat + sources 展示）
  - 当前已提供离线 mock 版本，后续接入只需替换发送逻辑对接 `/api/qa/ask`

## 3. 目录结构

- `backend-spring/`：主后端（Spring Boot）占位
- `rag-service/`：RAG/向量检索微服务（Node.js + TypeScript）占位
- `web-frontend/`：Web 问答前端（TypeScript + Vite，已可打开页面）
- `infra/`：基础设施与部署占位（docker-compose、k8s、env 模板等）
- `specs/`：接口与数据规范（OpenAPI、字段字典、错误码、返回结构等）
- `docs/`：设计/技术栈/实施方案文档
- `scripts/`：本地开发脚本（启动/停止/初始化）