# rag-service-node — RAG 问答核心服务

基于 Python 3.13 + FastAPI 的检索增强生成（RAG）问答引擎，负责从输入理解到答案生成的全链路处理，对接数据组知识图谱 API。

---

## 启动

```powershell
# 安装依赖
python -m pip install -r requirements.txt

# 启动服务（端口 8000）
python -m uvicorn app.main:app --reload
```

---

## RAG 管道流程

```
问题 → 规范化 → 上下文解析 → 实体抽取 → 意图分类 → 查询构建 → KG 检索 → 答案生成 → 溯源
```

---

## 目录结构

```
rag-service-node/
├── app/
│   ├── api/routes/          FastAPI 路由（ask / feedback / summary / health）
│   ├── core/                配置（Pydantic Settings 环境变量注入）
│   ├── models/              数据模型（api.py / domain.py / errors.py）
│   ├── orchestration/       管道编排（qa_pipeline.py）
│   ├── services/            服务模块
│   │   ├── input_understanding/  规范化/实体抽取/意图分类/上下文解析
│   │   ├── query_builder/        查询模板映射（16 个模板）
│   │   ├── kg_retrieval/         KG 检索（8 端点 hybrid 双模）
│   │   ├── answer_generation/    答案生成（rule 模板 + LLM 润色）
│   │   ├── llm/                  LLM 调用（DeepSeek）
│   │   └── logging_feedback/     日志与反馈记录
│   └── config/
│       ├── intent_rules.json      16 条意图规则配置
│       └── entity_aliases.json    22 条实体别名（中/英双语）
├── tests/
│   ├── test_pipeline.py         19 个单元测试（全意图 + 多轮 + 反馈）
│   ├── test_regression.py       36 个回归测试（questions.json 题集）
│   └── test_integration.py      33 个集成测试（真实 KG + LLM）
├── data/samples/questions.json  33 条测试题集
├── pyproject.toml               Ruff + pytest 配置
└── requirements.txt
```

---

## 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/qa/ask` | POST | 核心问答（question + session_id → answer + sources + facts） |
| `/api/qa/feedback` | POST | 反馈记录 |
| `/api/qa/summary` | GET | 统计摘要（意图分布/状态分布/失败清单） |

---

## 运行模式

| 模式 | 环境变量 | 说明 |
|------|----------|------|
| mock | `qa_graph_backend=mock` | 本地假数据，用于开发/测试 |
| hybrid | `qa_graph_backend=hybrid` | 真实 KG API 优先，失败降级 mock（默认） |
| remote | `qa_graph_backend=remote` | 仅真实 KG API，失败报错 |

```powershell
# 使用 mock 模式运行
$env:qa_graph_backend="mock"
python -m uvicorn app.main:app --reload
```

---

## 核心能力

| 模块 | 覆盖 |
|------|------|
| 意图分类 | 16 类（12 简单 + 4 复杂），关键词打分 + 实体加分 |
| 实体抽取 | 4 类实体（文物/博物馆/朝代/作者），22 条别名，中/英双语 |
| KG 检索 | 8 个数据组 API 端点，JWT 鉴权，hybrid 降级 |
| 答案生成 | rule 模式（16 类模板，~20ms）/ auto 模式（LLM 润色，~3.5s） |
| 多轮对话 | 代词指代消解 + 话题切换 + 30min 超时 |
| 中/英文 | 自动检测语种，lang=zh / lang=en |

---

## 测试

```powershell
# 全量测试
python -m pytest tests/ -v                    # 55 用例（单元 + 回归）
python -m pytest tests/test_integration.py -v  # 33 用例（真实 KG + LLM）

# 代码质量
ruff check .          # 静态检查
ruff format --check . # 格式检查
```

---

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `qa_graph_backend` | KG 后端模式 | `hybrid` |
| `qa_llm_backend` | LLM 后端模式 | `mock` |
| `qa_llm_api_url` | LLM API 地址 | DeepSeek |
| `qa_llm_api_key` | LLM API 密钥 | — |
| `qa_kg_api_key` | KG API JWT 令牌 | — |

完整配置见 `.env` 文件。

---

## 技术栈

- Python 3.13 · FastAPI · Pydantic
- Uvicorn（ASGI 服务器）
- Ruff（lint + format）
- pytest（测试框架）
