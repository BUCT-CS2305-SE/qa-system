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

export type Message = { role: 'user' | 'assistant'; text: string; meta?: QAResponse };
