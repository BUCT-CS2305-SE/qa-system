export type Source = { sourceName: string; detailUrl?: string };
export type Fact = { key: string; value: string };
export type QAResponse = {
  requestId?: string;
  answer: string;
  noData?: boolean;
  sources?: Source[];
  facts?: Fact[];
};

export type Message = { role: 'user' | 'assistant'; text: string; meta?: QAResponse };
