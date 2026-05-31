export type BackendSource = { source_name?: string; detail_url?: string };
export type BackendFact = {
  subject?: string;
  predicate?: string;
  object?: string;
  source_name?: string;
  source_url?: string;
};

export type BackendAskResponse = {
  request_id?: string;
  trace_id?: string;
  status?: 'ok' | 'clarify' | 'no_data' | 'error';
  code?: number;
  intent?: string;
  answer?: string;
  facts?: BackendFact[];
  sources?: BackendSource[];
  source?: BackendSource | null;
  llm_note?: string | null;
  confidence?: number;
};

export type BackendFeedbackResponse = {
  status: string;
  code: number;
  message: string;
};

export type BackendHistoryItem = {
  id: number;
  requestId: string;
  sessionId: string;
  question: string;
  answer: string;
  noData: boolean;
  sources: string;
  facts: string;
  intent: string;
  status: string;
  confidence: number;
  createdAt: string;
};

const BASE_URL = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8081';

export async function askBackend(
  question: string,
  sessionId?: string,
  timeoutMs = 30000,
  extra?: Record<string, unknown>
): Promise<BackendAskResponse | null> {
  const controller = new AbortController();
  const timerId = window.setTimeout(() => controller.abort(), timeoutMs);
  try {
    const bodyPayload = {
      question,
      session_id: sessionId,
      mode: 'auto',
      ...(extra || {})
    };
    const response = await fetch(`${BASE_URL}/api/qa/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(bodyPayload),
      signal: controller.signal
    });
    if (!response.ok) {
      console.error('ask failed', response.status, await response.text());
      return null;
    }
    // return raw json; calling code will adapt fields
    return (await response.json()) as BackendAskResponse;
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') {
      console.warn('ask request aborted (timeout)');
    } else {
      console.error('ask request error', error);
    }
    return null;
  } finally {
    window.clearTimeout(timerId);
  }
}

export async function sendBackendFeedback(
  traceId: string,
  helpful: boolean,
  comment?: string
): Promise<BackendFeedbackResponse | null> {
  try {
    const response = await fetch(`${BASE_URL}/api/qa/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        trace_id: traceId,
        helpful,
        comment
      })
    });
    if (!response.ok) {
      console.error('feedback failed', response.status, await response.text());
      return null;
    }
    return (await response.json()) as BackendFeedbackResponse;
  } catch (error: unknown) {
    console.error('feedback request error', error);
    return null;
  }
}

export async function fetchHistory(
  _sessionId: string,
  _limit = 20
): Promise<BackendHistoryItem[]> {
  try {
    // backend currently exposes summary rather than per-session history; return empty list to avoid 404
    const response = await fetch(`${BASE_URL}/api/qa/summary`);
    if (!response.ok) {
      console.warn('history/summary fetch failed', response.status);
      return [];
    }
    // If summary exists, we don't have a compatible history format yet - return empty array
    return [];
  } catch (error: unknown) {
    console.error('history fetch error', error);
    return [];
  }
}

// 调用外部 AI 用于润色（API URL 与 KEY 由 Vite 环境变量配置）
export async function callAiPolish(payload: { question: string; answer?: string; facts?: BackendFact[]; sources?: BackendSource[] }, timeoutMs = 20000): Promise<string | null> {
  const aiUrl = import.meta.env.VITE_AI_API_URL;
  if (!aiUrl) {
    return null;
  }
  const apiKey = import.meta.env.VITE_AI_API_KEY;
  try {
    const controller = new AbortController();
    const timerId = window.setTimeout(() => controller.abort(), timeoutMs);
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (apiKey) headers['Authorization'] = `Bearer ${apiKey}`;
    const resp = await fetch(aiUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
      signal: controller.signal
    });
    window.clearTimeout(timerId);
    if (!resp.ok) {
      console.error('AI polish call failed', resp.status, await resp.text());
      return null;
    }
    const data = await resp.json();
    // expect data to contain { text: 'polished answer' } or similar; caller will handle null
    return data.text || data.result || null;
  } catch (e) {
    console.error('AI polish error', e);
    return null;
  }
}
