# 前端调用示例（TypeScript）

本文件包含使用 fetch 与 axios 调用后端接口的示例，包括 `/api/qa/ask`、`/api/qa/history/list` 与反馈接口的例子。可直接复制到前端项目中做联调。

注意：示例中的 `BASE_URL` 需根据实际后端地址配置（例如 `http://localhost:8081`）。

---

## 类型定义（TypeScript）

```ts
export type AskRequest = {
  question: string;
  sessionId?: string;
};

export type Source = { sourceName: string; detailUrl: string };
export type Fact = { key: string; value: string };

export type AskResponse = {
  requestId: string;
  answer: string;
  noData: boolean;
  sources: Source[];
  facts: Fact[];
};

export type HistoryDto = {
  id: number;
  requestId: string;
  sessionId?: string;
  question: string;
  answer: string;
  noData: boolean;
  sources: string; // raw JSON
  facts: string; // raw JSON
  createdAt: string;
};
```

---

## 用 fetch 调用（带超时）

```ts
const BASE_URL = process.env.REACT_APP_API_BASE || '';

export async function fetchAsk(question: string, sessionId?: string, timeoutMs = 15000): Promise<AskResponse | null> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${BASE_URL}/api/qa/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, sessionId }),
      signal: controller.signal,
    });
    if (!res.ok) {
      console.error('ask failed', res.status, await res.text());
      return null;
    }
    const data = (await res.json()) as AskResponse;
    return data;
  } catch (err) {
    if ((err as any).name === 'AbortError') {
      console.warn('ask request aborted (timeout)');
    } else {
      console.error('ask request error', err);
    }
    return null;
  } finally {
    clearTimeout(id);
  }
}

export async function fetchHistory(sessionId: string, limit = 20): Promise<HistoryDto[] | null> {
  try {
    const res = await fetch(`${BASE_URL}/api/qa/history/list?sessionId=${encodeURIComponent(sessionId)}&limit=${limit}`);
    if (!res.ok) {
      console.error('history fetch failed', res.status);
      return null;
    }
    const data = (await res.json()) as HistoryDto[];
    return data;
  } catch (err) {
    console.error('history request error', err);
    return null;
  }
}
```

---

## 用 axios 调用（示例）

```ts
// 需安装 axios：npm install axios
import axios from 'axios';

const axiosClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE || '',
  timeout: 15000,
});

export async function axiosAsk(question: string, sessionId?: string): Promise<AskResponse | null> {
  try {
    const res = await axiosClient.post<AskResponse>('/api/qa/ask', { question, sessionId });
    return res.data;
  } catch (err) {
    console.error('axios ask error', err);
    return null;
  }
}

export async function axiosHistory(sessionId: string, limit = 20): Promise<HistoryDto[] | null> {
  try {
    const res = await axiosClient.get<HistoryDto[]>(`/api/qa/history/list`, { params: { sessionId, limit } });
    return res.data;
  } catch (err) {
    console.error('axios history error', err);
    return null;
  }
}
```

---

## 反馈接口示例

```ts
export async function sendFeedback(requestId: string, helpful: boolean, comment?: string) {
  try {
    const payload = { requestId, helpful, comment };
    const res = await fetch(`${BASE_URL}/api/qa/feedback`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    return res.ok;
  } catch (err) {
    console.error('feedback error', err);
    return false;
  }
}
```

---

## 使用建议

- 前端应在收到 `AskResponse.requestId` 后将 `sessionId` 与 `requestId` 一并保存，便于提交反馈或追踪问题。
- history 接口返回的 `sources`/`facts` 为字符串化 JSON（后端当前实现）；前端在展示前需要 JSON.parse。
- 推荐在开发环境把 `BASE_URL` 指向 `http://localhost:8081`（或实际后端地址）。

如需，我可以把 `backendClient.ts` TypeScript 文件直接创建到 `web-frontend/src/api/` 目录中。
