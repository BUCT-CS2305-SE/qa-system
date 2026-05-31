import { askBackend, fetchHistory } from '@/api/backendClient';

export type Source = { source_name: string; detail_url?: string };
export type Fact = { key: string; value: string; evidence?: string };
export type QAResponse = {
  request_id?: string;
  answer: string;
  no_data?: boolean;
  sources?: Source[];
  facts?: Fact[];
  intent?: string;
  status?: string;
  confidence?: number;
  llm_note?: string | null;
};

export async function ask(question: string, sessionId?: string, _mode: string = 'auto'): Promise<QAResponse> {
  const response = await askBackend(question, sessionId);
  if (!response) {
    return {
      answer: '问答服务暂时不可用，请稍后重试。',
      no_data: true,
      sources: [],
      facts: [],
      status: 'error'
    };
  }

  return {
    request_id: response.trace_id,
    answer: response.answer,
    no_data: response.status === 'no_data',
    sources: response.source.map((item) => ({
      source_name: item.name,
      detail_url: item.url
    })),
    facts: response.facts.map((item) => ({
      key: item.predicate,
      value: item.object,
      evidence: item.source_name ?? item.subject
    })),
    intent: response.intent,
    status: response.status,
    confidence: response.confidence,
    llm_note: response.llm_note
  };
}

export type HistoryItem = { id: string; title: string; last: string };

export async function getHistory(sessionId: string, _limit = 20): Promise<HistoryItem[]> {
  try {
    const items = await fetchHistory(sessionId, _limit);
    if (items.length === 0) {
      return [{ id: sessionId, title: '当前会话', last: '尚无历史记录，开始提问吧' }];
    }
    return items.map((it) => ({
      id: String(it.id),
      title: it.question.length > 30 ? it.question.substring(0, 30) + '...' : it.question,
      last: it.answer.length > 40 ? it.answer.substring(0, 40) + '...' : it.answer
    }));
  } catch {
    return [{ id: sessionId, title: '当前会话', last: '后端已接入，可直接测试问答链路' }];
  }
}
