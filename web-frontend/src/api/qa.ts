import { askBackend, fetchHistory, callAiPolish } from '@/api/backendClient';

export type Source = { source_name?: string; detail_url?: string };
export type Fact = { key?: string; value?: string; evidence?: string };
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
  trace_id?: string;
};

function classifyQuestion(question: string): string {
  const q = question.toLowerCase();
  if (/图片|照片|以图搜图|图像|image|photo/.test(q)) return 'image_search';
  if (/尺寸|大小|长|高|宽|cm|mm/.test(q)) return 'artifact_dimensions';
  if (/哪家|在哪|收藏|现藏|在哪里|博物馆/.test(q)) return 'artifact_museum';
  if (/材质|材料|材质是/.test(q)) return 'artifact_material';
  if (/作者|画家|是谁|author|artist/.test(q)) return 'painting_author';
  return 'general';
}

export async function ask(question: string, sessionId?: string): Promise<QAResponse> {
  const intent = classifyQuestion(question);
  // choose mode: prefer rule for specific intents, auto for general QA
  const mode = intent === 'general' ? 'auto' : 'rule';

  const response = await askBackend(question, sessionId, 30000, { intent, mode });
  if (!response) {
    return {
      answer: '问答服务暂时不可用，请稍后重试。',
      no_data: true,
      sources: [],
      facts: [],
      status: 'error'
    };
  }

  const sources = (response.sources || (response.source ? [response.source] : [])) as Source[];
  type BackendFact = { predicate?: string; key?: string; object?: string; value?: string; source_name?: string; subject?: string };
  const facts = (response.facts || []) as BackendFact[];

  let answerText = response.answer || '';

  // 如果配置了外部 AI，则用其对问答结果进行润色
  try {
    const polished = await callAiPolish({ question, answer: answerText, facts: response.facts || [], sources: sources });
    if (polished) {
      answerText = polished;
    }
  } catch (e) {
    // 忽略润色错误，返回原始答案
    console.warn('AI polish failed', e);
  }

  return {
    request_id: response.request_id || response.trace_id,
    answer: answerText,
    no_data: response.status === 'no_data',
    sources: sources.map((item) => ({ source_name: item.source_name, detail_url: item.detail_url })),
    facts: facts.map((item) => ({ key: item.predicate || item.key, value: item.object || item.value, evidence: item.source_name || item.subject })),
    intent: response.intent || intent,
    status: response.status,
    confidence: response.confidence,
    llm_note: response.llm_note
  };
}

export type HistoryItem = { id: string; title: string; last: string; question: string; answer: string };

export async function getHistory(sessionId: string, _limit = 20): Promise<HistoryItem[]> {
  try {
    const items = await fetchHistory(sessionId, _limit);
    if (!items || items.length === 0) {
      return [{
        id: sessionId,
        title: '当前会话',
        last: '尚无历史记录，开始提问吧',
        question: '',
        answer: ''
      }];
    }
    return items.map((it) => ({
      id: String(it.id),
      title: it.question.length > 30 ? it.question.substring(0, 30) + '...' : it.question,
      last: it.answer.length > 40 ? it.answer.substring(0, 40) + '...' : it.answer,
      question: it.question,
      answer: it.answer
    }));
  } catch {
    return [{
      id: sessionId,
      title: '当前会话',
      last: '后端已接入，可直接测试问答链路',
      question: '',
      answer: ''
    }];
  }
}
