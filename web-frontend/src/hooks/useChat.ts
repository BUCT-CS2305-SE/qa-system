import { useCallback, useEffect, useRef, useState } from 'react';
import { ask, getHistory } from '@/api/qa';
import { sendBackendFeedback } from '@/api/backendClient';
import type { QAResponse } from '@/api/qa';

export type Message = { role: 'user' | 'assistant'; text: string; meta?: QAResponse };

type ConvMessages = {
  sessionId: string;
  messages: Message[];
  loading: boolean;
  /**
   * 最后活跃时间戳（ms）。用于前端本地 TTL 清理。
   */
  lastActiveAt?: number;
};

const STORAGE_KEY = 'qa_conversations';

// 会话本地 TTL：5 天（满足“3~5天”诉求，取上限更不易误删）
const CONV_TTL_MS = 5 * 24 * 60 * 60 * 1000;

// 每个会话最大消息数：复杂/长对话给更大窗口；同时避免 localStorage 无限制膨胀
const MAX_MESSAGES_PER_CONV = 500;

function nowMs(): number {
  return Date.now();
}

function generateId(ts: number): string {
  return 'conv_' + ts + '_' + Math.random().toString(36).substring(2, 6);
}

function generateSessionId(ts: number): string {
  return 'sess_' + ts + '_' + Math.random().toString(36).substring(2, 8);
}

function loadConversationsFromStorage(): Record<string, ConvMessages> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};

    const parsed = JSON.parse(raw) as Record<string, unknown>;
    const result: Record<string, ConvMessages> = {};
    const now = nowMs();

    for (const [id, data] of Object.entries(parsed)) {
      const d = data as { sessionId: string; messages: { role: string; text: string; meta: QAResponse | null }[]; lastActiveAt?: number };

      // TTL 清理：超过 CONV_TTL_MS 的会话直接跳过（不载入）
      const lastActive = typeof d.lastActiveAt === 'number' ? d.lastActiveAt : undefined;
      if (lastActive != null && now - lastActive > CONV_TTL_MS) {
        continue;
      }

      result[id] = {
        sessionId: d.sessionId,
        messages: (d.messages || []).map((m) => ({
          role: m.role as 'user' | 'assistant',
          text: m.text,
          meta: m.meta || undefined,
        })),
        loading: false,
        lastActiveAt: lastActive,
      };
    }

    return result;
  } catch {
    // ignore parse errors and treat as empty
    return {};
  }
}

function saveConversationsToStorage(convs: Record<string, ConvMessages>) {
  try {
    const serializable: Record<string, unknown> = {};
    for (const [id, c] of Object.entries(convs)) {
      serializable[id] = { sessionId: c.sessionId, messages: c.messages, lastActiveAt: c.lastActiveAt };
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(serializable));
  } catch {
    // ignore storage quota / serialization errors
  }
}

function trimMessages(messages: Message[]): Message[] {
  if (messages.length <= MAX_MESSAGES_PER_CONV) return messages;
  return messages.slice(messages.length - MAX_MESSAGES_PER_CONV);
}

function gcConversations(convs: Record<string, ConvMessages>): Record<string, ConvMessages> {
  const now = nowMs();
  const next: Record<string, ConvMessages> = {};

  for (const [id, c] of Object.entries(convs)) {
    const lastActive = c.lastActiveAt ?? now;
    if (now - lastActive <= CONV_TTL_MS) {
      next[id] = c;
    }
  }

  return next;
}

export function useChat() {
  const [conversations, setConversations] = useState<Record<string, ConvMessages>>(() => {
    // 首次加载时做一次 GC
    return gcConversations(loadConversationsFromStorage());
  });
  const [activeId, setActiveId] = useState<string>('');

  // ref 只在 effect 中同步，避免 lint: "Cannot update ref during render"
  const conversationsRef = useRef<Record<string, ConvMessages>>(conversations);
  useEffect(() => {
    conversationsRef.current = conversations;
  }, [conversations]);

  const [feedbackState, setFeedbackState] = useState<Record<string, Record<number, 'helpful' | 'unhelpful'>>>({});

  const persist = useCallback((convs: Record<string, ConvMessages>) => {
    saveConversationsToStorage(convs);
  }, []);

  // 定时 GC：每小时清理一次过期会话（前端自动刷新/清掉的核心机制）
  useEffect(() => {
    const timer = window.setInterval(() => {
      setConversations((prev) => {
        const next = gcConversations(prev);
        if (Object.keys(next).length !== Object.keys(prev).length) {
          persist(next);
        }
        return next;
      });
    }, 60 * 60 * 1000);

    return () => window.clearInterval(timer);
  }, [persist]);

  const touchConversation = useCallback((convs: Record<string, ConvMessages>, convId: string) => {
    const c = convs[convId];
    if (!c) return convs;
    const next = {
      ...convs,
      [convId]: {
        ...c,
        lastActiveAt: nowMs(),
      },
    };
    return next;
  }, []);

  const createConversation = useCallback(() => {
    const ts = nowMs();
    const id = generateId(ts);
    const sessionId = generateSessionId(ts);

    setConversations((prev) => {
      const next = {
        ...prev,
        [id]: { sessionId, messages: [], loading: false, lastActiveAt: ts },
      };
      persist(next);
      return next;
    });

    setActiveId(id);
    return id;
  }, [persist]);

  const deleteConversation = useCallback((id: string) => {
    setConversations((prev) => {
      const next = { ...prev };
      delete next[id];
      persist(next);
      return next;
    });
    if (activeId === id) {
      const remaining = Object.keys(conversationsRef.current).filter((k) => k !== id);
      setActiveId(remaining[0] || '');
    }
  }, [activeId, persist]);

  const switchConversation = useCallback((id: string) => {
    setActiveId(id);
    setConversations((prev) => {
      const next = touchConversation(prev, id);
      persist(next);
      return next;
    });
  }, [persist, touchConversation]);

  const selectOrCreate = useCallback(() => {
    if (activeId && conversationsRef.current[activeId]) return activeId;
    return createConversation();
  }, [activeId, createConversation]);

  const getActive = useCallback((): ConvMessages | null => {
    if (!activeId || !conversations[activeId]) return null;
    return conversations[activeId];
  }, [activeId, conversations]);

  const activeMessages = getActive()?.messages ?? [];
  const activeLoading = getActive()?.loading ?? false;
  const activeSessionId = getActive()?.sessionId ?? '';

  useEffect(() => {
    if (!activeId || !activeSessionId) return;
    const conv = conversations[activeId];
    if (!conv || conv.messages.length > 0) return;

    getHistory(activeSessionId).then((items) => {
      if (items.length === 0) return;

      const msgs: Message[] = [];
      for (const item of items) {
        if (item.question) {
          msgs.push({ role: 'user', text: item.question });
        }
        if (item.answer) {
          msgs.push({ role: 'assistant', text: item.answer });
        }
      }

      if (msgs.length > 0) {
        setConversations((prev) => {
          const next = {
            ...prev,
            [activeId]: {
              ...prev[activeId],
              messages: trimMessages(msgs),
              lastActiveAt: nowMs(),
            },
          };
          persist(next);
          return next;
        });
      }
    });
  }, [activeId, activeSessionId, conversations, persist]);

  const send = useCallback(async (text: string) => {
    const convId = selectOrCreate();
    const conv = conversationsRef.current[convId];
    if (!conv) return;

    const userMsg: Message = { role: 'user', text };

    setConversations((prev) => {
      const current = prev[convId];
      const updatedMessages = trimMessages([...(current?.messages || []), userMsg]);
      const next = {
        ...prev,
        [convId]: {
          ...(current || { sessionId: conv.sessionId, messages: [], loading: false }),
          messages: updatedMessages,
          loading: true,
          lastActiveAt: nowMs(),
        },
      };
      persist(next);
      return next;
    });

    try {
      const resp = await ask(text, conv.sessionId);
      const assistant: Message = { role: 'assistant', text: resp.answer, meta: resp };
      setConversations((prev) => {
        const current = prev[convId];
        const updatedMessages = trimMessages([...(current?.messages || []), assistant]);
        const next = {
          ...prev,
          [convId]: {
            ...(current || { sessionId: conv.sessionId, messages: [], loading: false }),
            messages: updatedMessages,
            loading: false,
            lastActiveAt: nowMs(),
          },
        };
        persist(next);
        return next;
      });
    } catch {
      setConversations((prev) => {
        const current = prev[convId];
        const next = {
          ...prev,
          [convId]: {
            ...(current || { sessionId: conv.sessionId, messages: [], loading: false }),
            loading: false,
            lastActiveAt: nowMs(),
          },
        };
        persist(next);
        return next;
      });
    }
  }, [selectOrCreate, persist]);

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

  const convList = Object.entries(conversations).map(([id, c]) => {
    const createdAt = Number.parseInt(id.split('_')[1] || '0', 10) || 0;
    return {
      id,
      title: c.messages.length > 0
        ? (c.messages[0]?.text?.slice(0, 20) || '新对话')
        : '新对话',
      lastMessage: c.messages.length > 0
        ? c.messages[c.messages.length - 1]?.text?.slice(0, 30) || ''
        : '',
      createdAt,
    };
  });

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
