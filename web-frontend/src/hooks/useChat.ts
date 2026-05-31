import { useCallback, useEffect, useState } from 'react';
import { ask, getHistory } from '@/api/qa';
import type { Message, QAResponse } from '@/types/qa';

export function useChat(sessionId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getHistory(sessionId).then(() => {
      // history loaded
    });
  }, [sessionId]);

  const send = useCallback(async (text: string) => {
    const userMsg: Message = { role: 'user', text };
    setMessages((s) => [...s, userMsg]);
    setLoading(true);
    try {
      const resp: QAResponse = await ask(text, sessionId);
      const assistant: Message = { role: 'assistant', text: resp.answer, meta: resp };
      setMessages((s) => [...s, assistant]);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  return { messages, send, loading, setMessages };
}
