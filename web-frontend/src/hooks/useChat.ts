import { useCallback, useEffect, useState } from 'react';
import { fetchAsk, fetchHistory } from '@/api/backendClient';
import type { Message, QAResponse } from '@/types/qa';

function generateSessionId(): string {
  const stored = sessionStorage.getItem('qa_sessionId');
  if (stored) return stored;
  const id = 'sess_' + Date.now() + '_' + Math.random().toString(36).slice(2, 9);
  sessionStorage.setItem('qa_sessionId', id);
  return id;
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(generateSessionId);

  useEffect(() => {
    fetchHistory(sessionId).then((list) => {
      if (list && list.length > 0) {
        const msgs: Message[] = [];
        for (const h of list) {
          msgs.push({ role: 'user', text: h.question });
          msgs.push({
            role: 'assistant',
            text: h.answer,
            meta: {
              answer: h.answer,
              noData: h.noData,
              sources: parseSources(h.sources),
              facts: parseFacts(h.facts)
            }
          });
        }
        setMessages(msgs);
      }
    });
  }, [sessionId]);

  const send = useCallback(async (text: string) => {
    const userMsg: Message = { role: 'user', text };
    setMessages((s) => [...s, userMsg]);
    setLoading(true);
    try {
      const resp = await fetchAsk(text, sessionId);
      if (resp) {
        const assistant: Message = { role: 'assistant', text: resp.answer, meta: resp };
        setMessages((s) => [...s, assistant]);
      } else {
        const errMsg: Message = { role: 'assistant', text: '请求失败，请检查后端服务是否启动。' };
        setMessages((s) => [...s, errMsg]);
      }
    } catch {
      const errMsg: Message = { role: 'assistant', text: '网络错误，请稍后重试。' };
      setMessages((s) => [...s, errMsg]);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  return { messages, send, loading, setMessages, sessionId };
}

function parseSources(raw: string): QAResponse['sources'] {
  if (!raw) return [];
  try {
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

function parseFacts(raw: string): QAResponse['facts'] {
  if (!raw) return [];
  try {
    return JSON.parse(raw);
  } catch {
    return [];
  }
}
