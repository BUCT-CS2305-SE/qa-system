export type BackendSource = { name: string; url: string };
export type BackendFact = {
  subject: string;
  predicate: string;
  object: string;
  source_name?: string;
  source_url?: string;
};

export type BackendAskResponse = {
  status: 'ok' | 'clarify' | 'no_data';
  code: number;
  intent: string;
  answer: string;
  facts: BackendFact[];
  source: BackendSource[];
  llm_note?: string | null;
  confidence: number;
  trace_id: string;
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
  timeoutMs = 30000
): Promise<BackendAskResponse | null> {
  const controller = new AbortController();
  const timerId = window.setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(`${BASE_URL}/api/qa/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        session_id: sessionId,
        mode: 'auto'
      }),
      signal: controller.signal
    });
    if (!response.ok) {
      console.error('ask failed', response.status, await response.text());
      return null;
    }
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
  sessionId: string,
  limit = 20
): Promise<BackendHistoryItem[]> {
  try {
    const response = await fetch(
      `${BASE_URL}/api/qa/history?sessionId=${encodeURIComponent(sessionId)}&limit=${limit}`
    );
    if (!response.ok) {
      console.error('history fetch failed', response.status);
      return [];
    }
    return (await response.json()) as BackendHistoryItem[];
  } catch (error: unknown) {
    console.error('history fetch error', error);
    return [];
  }
}
