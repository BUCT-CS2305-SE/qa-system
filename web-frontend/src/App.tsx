import React, { useState, useMemo } from 'react';

import './styles/app.css';

import ChatHeader from './components/ChatHeader';
import SideHistory from './components/SideHistory';
import ChatBox from './components/ChatBox';
import ChatComposer from './components/ChatComposer';
import { useChat } from './hooks/useChat';
import { getHistory } from './api/qa';

export type HistoryItem = { id: string; title: string; last: string };

function generateSessionId(): string {
  return 'sess_' + Date.now() + '_' + Math.random().toString(36).substring(2, 8);
}

export default function App() {
  const [question, setQuestion] = useState('');
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const sessionId = useMemo(() => generateSessionId(), []);

  const { messages, send, loading } = useChat(sessionId);

  React.useEffect(() => {
    getHistory(sessionId).then((h: HistoryItem[]) => setHistory(h));
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
            <div className="fgBrandSub">演示模式（Spring + RAG）</div>
          </div>
        </div>

        <SideHistory list={history} />

        <div className="fgSideSection">
          <div className="fgSideSectionTitle">提示</div>
          <div className="fgSideHint">
            请先启动 rag-service-node (端口8000) 和 backend-spring (端口8081) 再测试。
          </div>
        </div>

        <div className="fgSideFooter">
          <div className="fgSideFooterItem">
            <span className="dot online"></span>
            <span>UI：Spring → RAG 问答链路</span>
          </div>
        </div>
      </aside>

      <main className="fgMain">
        <ChatHeader
          title="文物知识问答"
          desc="基于 KG + RAG（Spring后端代理规则版问答服务）"
          badges={['Neo4j', 'RAG']}
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
