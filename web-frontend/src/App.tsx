import React, { useState } from 'react';

import './styles/app.css';

import ChatHeader from './components/ChatHeader';
import SideHistory from './components/SideHistory';
import ChatBox from './components/ChatBox';
import ChatComposer from './components/ChatComposer';
import { useChat } from './hooks/useChat';
import { fetchHistory } from './api/backendClient';

export type HistoryItem = { id: string; title: string; last: string };

export default function App() {
  const [question, setQuestion] = useState('');
  const [history, setHistory] = useState<HistoryItem[]>([]);

  const { messages, send, loading, sessionId } = useChat();

  React.useEffect(() => {
    fetchHistory(sessionId).then((list) => {
      if (list && list.length > 0) {
        const items: HistoryItem[] = list.map((h) => ({
          id: String(h.id),
          title: h.question.length > 30 ? h.question.slice(0, 30) + '...' : h.question,
          last: h.answer.length > 50 ? h.answer.slice(0, 50) + '...' : h.answer
        }));
        setHistory(items);
      }
    });
  }, [sessionId]);

  async function handleAsk() {
    const q = question.trim();
    if (!q) return;
    await send(q);
    setQuestion('');
  }

  return (
    <div className="fgLayout">
      <aside className="fgSidebar">
        <div className="fgBrand">
          <div className="fgBrandLogo" />
          <div>
            <div className="fgBrandTitle">文物问答子系统</div>
            <div className="fgBrandSub">Spring Boot + React 联调模式</div>
          </div>
        </div>

        <SideHistory list={history} />

        <div className="fgSideSection">
          <div className="fgSideSectionTitle">提示</div>
          <div className="fgSideHint">
            后端 API 地址：<code>/api/qa/ask</code>
          </div>
        </div>

        <div className="fgSideFooter">
          <div className="fgSideFooterItem">
            <span className="dot online"></span>
            <span>Session: {sessionId.slice(0, 12)}...</span>
          </div>
        </div>
      </aside>

      <main className="fgMain">
        <ChatHeader
          title="文物知识问答"
          desc="基于 KG + RAG（Spring Boot 后端）"
          badges={['Neo4j', 'pgvector']}
        />

        <ChatBox messages={messages} />

        <ChatComposer
          value={question}
          onChange={(v: string) => setQuestion(v)}
          onSend={handleAsk}
          sending={loading}
        />
      </main>
    </div>
  );
}
