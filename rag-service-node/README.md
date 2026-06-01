# rag-service-node

本目录原本是总仓中的 RAG 微服务占位目录，现已先集成一套可运行的 Python/FastAPI 问答服务原型，作为组内开发和联调基线。

## 当前定位

- 目录名保留为 `rag-service-node`，以对齐总仓既有结构
- 当前实现不是 Node.js 成品，而是迁入的 Python 原型框架
- 目标是先跑通问答链路，再逐步迁移或重构为 Node.js + TypeScript 版本

## 当前已集成内容

- FastAPI 服务入口
- 输入理解模块：标准化、实体抽取、意图识别、上下文消歧占位
- 查询构建模块：查询模板与参数映射
- 图谱检索模块：mock 数据版检索服务
- 答案生成模块：规则版答案组织与来源输出
- 日志反馈模块：内存版日志与反馈记录
- 单元测试

## 目录结构

- `app/`：服务主代码
- `data/`：样例数据
- `tests/`：基础测试
- `requirements.txt`：Python 依赖

## 当前技术栈

- Python 3.14
- FastAPI
- Pydantic / pydantic-settings
- Uvicorn

## 快速启动

安装依赖：

```bash
c:/python314/python.exe -m pip install -r requirements.txt
```

启动服务：

```bash
c:/python314/python.exe -m uvicorn app.main:app --reload
```

运行测试：

```bash
c:/python314/python.exe -m unittest discover -s tests -v
```

## 当前接口

- `GET /api/health`
- `POST /api/qa/ask`
- `POST /api/qa/feedback`

## 当前适合承担的职责

- 问题标准化与输入理解
- 意图分类、实体识别、别名归一
- 查询模板映射
- 规则版问答主流程联调
- 与 `backend-spring` 的接口对接前验证

## 尚未完成的能力

- 真实向量化、向量召回与 pgvector 检索
- Mongo / Redis 接入
- FastGPT 检索链路复用
- 真实 LLM / RAG 生成
- Node.js + TypeScript 正式实现

## 推荐迁移策略

建议按下面顺序演进，而不是一次性推倒重来：

1. 继续在当前 Python 原型上把接口、字段、返回结构稳定下来。
2. 将 `backend-spring -> rag-service-node` 的调用链先联通。
3. 在保证接口不变的前提下，把 mock 检索替换成真实图谱或文档检索实现。
4. 最后再决定是保留 Python 服务，还是平滑迁移到 Node.js + TypeScript。

## 备注

如果组内已经决定最终必须落 Node.js + TypeScript，可将当前目录视为“接口与流程原型”，重点复用：

- 目录分层方式
- 输入理解到答案输出的流水线设计
- 请求与响应模型
- 错误码和测试思路
