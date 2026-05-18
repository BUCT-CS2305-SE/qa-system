// API client for frontend: provides both fetch and axios implementations

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
  sources: string; // raw JSON string
  facts: string; // raw JSON string
  createdAt: string;
};

// Use Vite runtime env (import.meta.env).
const BASE_URL = import.meta.env.VITE_API_BASE ?? '';

// ------------------ Fetch implementation ------------------
export async function fetchAsk(
  question: string,
  sessionId?: string,
  timeoutMs = 15000
): Promise<AskResponse | null> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${BASE_URL}/api/qa/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, sessionId }),
      signal: controller.signal
    });
    if (!res.ok) {
      console.error('ask failed', res.status, await res.text());
      return null;
    }
    const data = (await res.json()) as AskResponse;
    return data;
  } catch (err: unknown) {
    if (err instanceof Error && err.name === 'AbortError') {
      console.warn('ask request aborted (timeout)');
    } else if (err instanceof Error) {
      console.error('ask request error', err.message);
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
    const res = await fetch(
      `${BASE_URL}/api/qa/history/list?sessionId=${encodeURIComponent(sessionId)}&limit=${limit}`
    );
    if (!res.ok) {
      console.error('history fetch failed', res.status);
      return null;
    }
    const data = (await res.json()) as HistoryDto[];
    return data;
  } catch (err: unknown) {
    if (err instanceof Error) console.error('history request error', err.message);
    else console.error('history request error', err);
    return null;
  }
}

export async function sendFeedback(
  requestId: string,
  helpful: boolean,
  comment?: string
): Promise<boolean> {
  try {
    const payload = { requestId, helpful, comment };
    const res = await fetch(`${BASE_URL}/api/qa/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return res.ok;
  } catch (err: unknown) {
    if (err instanceof Error) console.error('feedback error', err.message);
    else console.error('feedback error', err);
    return false;
  }
}

// ------------------ Axios implementation ------------------
// Note: install axios in web-frontend to use these functions: npm install axios
import axios from 'axios';

const axiosClient = axios.create({
  baseURL: BASE_URL,
  timeout: 15000
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
    const res = await axiosClient.get<HistoryDto[]>('/api/qa/history/list', {
      params: { sessionId, limit }
    });
    return res.data;
  } catch (err) {
    console.error('axios history error', err);
    return null;
  }
}

export async function axiosSendFeedback(
  requestId: string,
  helpful: boolean,
  comment?: string
): Promise<boolean> {
  try {
    const payload = { requestId, helpful, comment };
    const res = await axiosClient.post('/api/qa/feedback', payload);
    return res.status >= 200 && res.status < 300;
  } catch (err) {
    console.error('axios feedback error', err);
    return false;
  }
}
