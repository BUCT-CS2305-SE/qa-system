import { useCallback, useEffect, useState } from 'react';
import { ask, getHistory } from '@/api/qa';
import { sendBackendFeedback } from '@/api/backendClient';
import type { QAResponse } from '@/api/qa';

export type Message = { role: 'user' | 'assistant'; text: string; meta?: QAResponse };

type ConvMessages = {
  sessionId: string;
  messages: Message[];
  loading: boolean;
};

export function useChat() {
  const [conversations, setConversations] = useState<Record<string, ConvMessages>>({});
  const [activeId, setActiveId] = useState<string>('');

  const [feedbackState, setFeedbackState] = useState<Record<string, Record<number, 'helpful' | 'unhelpful'>>>({});

  function generateId(): string {
    return 'conv_' + Date.now() + '_' + Math.random().toString(36).substring(2, 6);
  }

  function generateSessionId(): string {
    return 'sess_' + Date.now() + '_' + Math.random().toString(36).substring(2, 8);
  }

  const createConversation = useCallback(() => {
    const id = generateId();
    const sessionId = generateSessionId();
    setConversations((prev: Record<string, ConvMessages>) => ({
      ...prev,
      [id]: { sessionId, messages: [], loading: false },
    }));
    setActiveId(id);
    return id;
  }, []);

  const deleteConversation = useCallback((id: string) => {
    setConversations((prev: Record<string, ConvMessages>) => {
      const next = { ...prev };
      delete next[id];
      return next;
    });
    if (activeId === id) {
      const remaining = Object.keys(conversations).filter((k: string) => k !== id);
      setActiveId(remaining[0] || '');
    }
  }, [activeId, conversations]);

  const switchConversation = useCallback((id: string) => {
    setActiveId(id);
  }, []);

  const selectOrCreate = useCallback(() => {
    if (activeId && conversations[activeId]) return activeId;
    return createConversation();
  }, [activeId, conversations, createConversation]);

  const getActive = useCallback((): ConvMessages | null => {
    if (!activeId || !conversations[activeId]) return null;
    return conversations[activeId];
  }, [activeId, conversations]);

  const activeMessages = getActive()?.messages ?? [];
  const activeLoading = getActive()?.loading ?? false;
  const activeSessionId = getActive()?.sessionId ?? '';

  useEffect(() => {
    if (!activeId || !activeSessionId) return;
    getHistory(activeSessionId).then(() => {});
  }, [activeId, activeSessionId]);

  const send = useCallback(async (text: string) => {
    const convId = selectOrCreate();
    const conv = conversations[convId];
    if (!conv) return;

    const userMsg: Message = { role: 'user', text };

    setConversations((prev: Record<string, ConvMessages>) => ({
      ...prev,
      [convId]: {
        ...prev[convId],
        messages: [...prev[convId].messages, userMsg],
        loading: true,
      },
    }));

    try {
      const resp = await ask(text, conv.sessionId);
      const assistant: Message = { role: 'assistant', text: resp.answer, meta: resp };
      setConversations((prev: Record<string, ConvMessages>) => ({
        ...prev,
        [convId]: {
          ...prev[convId],
          messages: [...prev[convId].messages, assistant],
          loading: false,
        },
      }));
    } catch {
      setConversations((prev: Record<string, ConvMessages>) => ({
        ...prev,
        [convId]: {
          ...prev[convId],
          loading: false,
        },
      }));
    }
  }, [selectOrCreate, conversations]);

  const handleFeedback = useCallback(async (msgIdx: number, helpful: boolean) => {
    const conv = getActive();
    if (!conv || !conv.messages[msgIdx]) return;
    const meta = conv.messages[msgIdx].meta;
    const traceId = meta?.trace_id || meta?.request_id;
    if (!traceId) return;

    await sendBackendFeedback(traceId, helpful);

    setFeedbackState((prev) => ({
      ...prev,
      [activeId]: { ...(prev[activeId] || {}), [msgIdx]: helpful ? 'helpful' : 'unhelpful' },
    }));
  }, [getActive, activeId]);

  const convList = Object.entries(conversations).map(([id, c]) => ({
    id,
    title: c.messages.length > 0
      ? (c.messages[0]?.text?.slice(0, 20) || '新对话')
      : '新对话',
    lastMessage: c.messages.length > 0
      ? c.messages[c.messages.length - 1]?.text?.slice(0, 30) || ''
      : '',
    createdAt: parseInt(id.split('_')[1]) || Date.now(),
  }));

  return {
    conversations: convList,
    activeId,
    activeMessages,
    activeLoading,
    createConversation,
    deleteConversation,
    switchConversation,
    send,
    feedbackState: feedbackState[activeId] || {},
    handleFeedback,
  };
}
