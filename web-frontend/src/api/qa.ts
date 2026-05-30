import { askBackend } from '@/api/backendClient';

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

export async function ask(question: string, _mode: string = 'auto'): Promise<QAResponse> {
  const response = await askBackend(question);
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

export async function getHistory(_limit = 20) {
  return Promise.resolve([
    { id: 'local-session', title: '当前会话', last: '后端已接入，可直接测试问答链路' }
  ]);
}

export async function getSource(id: string) {
  return Promise.resolve({
    id,
    name: '来源详情',
    url: id,
    excerpt: '当前版本直接展示后端返回的来源链接。'
  });
}
