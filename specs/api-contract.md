# API 契约文档

版本：v1.0 | 基础 URL：`http://127.0.0.1:8081`

---

## 1. POST /api/qa/ask

### 请求

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `question` | string | 是 | 用户自然语言问题，最长500字符 |
| `session_id` | string | 否 | 会话标识，P2多轮使用时传入 |
| `mode` | string | 否 | 答案生成模式：`rule`(规则模板) / `auto`(LLM润色) / `llm`(纯LLM)，默认 `auto` |
| `intent` | string | 否 | 前端本地意图分类结果，后端可覆盖 |

```json
{
  "question": "女史箴图现藏于哪家博物馆？",
  "session_id": "sess_1717200000000_abc123",
  "mode": "rule"
}
```

### 响应

| 字段 | 类型 | 说明 |
|------|------|------|
| `request_id` | string | 本次请求唯一标识 |
| `answer` | string | 答案文本 |
| `no_data` | boolean | 是否为无数据兜底 |
| `sources` | array | 来源信息列表 |
| `sources[].source_name` | string | 来源名称（如博物馆名） |
| `sources[].detail_url` | string | 来源详情页链接 |
| `facts` | array | 检索到的事实列表 |
| `facts[].subject` | string | 事实主体 |
| `facts[].predicate` | string | 谓词 |
| `facts[].object` | string | 宾词 |
| `facts[].source_name` | string | 来源名称 |
| `facts[].source_url` | string | 来源链接 |
| `status` | string | 状态：`ok` / `no_data` / `clarify` |
| `code` | int | 状态码：2000(成功) / 2001(无数据) / 4001(未识别) / 4002(缺实体) / 5004(服务不可用) |
| `intent` | string | 识别到的意图 |
| `llm_note` | string/null | LLM生成标注 |
| `confidence` | float | 置信度 0.0~1.0 |
| `trace_id` | string | 跟踪ID，用于反馈关联 |

### Code定义

| Code | 含义 |
|------|------|
| 2000 | 成功 |
| 2001 | 暂无相关数据（no_data） |
| 4001 | 问题无法识别 |
| 4002 | 未抽取到关键实体 |
| 4003 | 知识图谱查询失败 |
| 5001 | LLM生成失败 |
| 5002 | 来源缺失 |
| 5003 | 内部错误 |
| 5004 | 问答服务暂时不可用 |

### 成功示例

```json
{
  "request_id": "t20240601_120000",
  "answer": "女史箴图现藏于大英博物馆。",
  "no_data": false,
  "sources": [
    {
      "source_name": "大英博物馆",
      "detail_url": "https://www.britishmuseum.org/collection"
    }
  ],
  "facts": [
    {
      "subject": "女史箴图",
      "predicate": "museum",
      "object": "大英博物馆",
      "source_name": "大英博物馆",
      "source_url": "https://www.britishmuseum.org/collection"
    }
  ],
  "status": "ok",
  "code": 2000,
  "intent": "artifact_museum",
  "llm_note": null,
  "confidence": 0.95,
  "trace_id": "t20240601_120000"
}
```

### no_data 示例

```json
{
  "request_id": "t20240601_120001",
  "answer": "暂无相关数据",
  "no_data": true,
  "sources": [],
  "facts": [],
  "status": "no_data",
  "code": 2001,
  "intent": "artifact_material",
  "llm_note": null,
  "confidence": 0.0,
  "trace_id": "t20240601_120001"
}
```

---

## 2. POST /api/qa/feedback

### 请求

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `trace_id` | string | 是 | 关联的问答 `trace_id` |
| `helpful` | boolean | 是 | 是否有帮助 |
| `comment` | string | 否 | 补充说明 |

```json
{
  "trace_id": "t20240601_120000",
  "helpful": true,
  "comment": "回答准确"
}
```

### 响应

```json
{
  "status": "ok",
  "code": 2000,
  "message": "反馈已记录"
}
```

---

## 3. GET /api/health

### 响应

```json
{
  "status": "ok"
}
```

| 状态值 | 含义 |
|--------|------|
| `ok` | 服务正常 |
| `degraded` | 部分降级（Neo4j/LLM不通但核心可用） |

---

## 4. 鉴权

所有 `/api/qa/*` 请求需携带请求头：

```
X-Api-Key: <apikey>
```

开发环境默认 key：`qa-demo-key`

---

## 5. 限流

- 规则：同一 IP 在 60 秒内最多 60 次请求
- 超出返回 HTTP 429：
```json
{
  "error": "rate_limit_exceeded",
  "message": "请求过于频繁，请稍后重试"
}
```
