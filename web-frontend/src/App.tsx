import React, { useState } from 'react';

import './styles/app.css';

import ChatHeader from './components/ChatHeader';
import SideHistory from './components/SideHistory';
import ChatBox from './components/ChatBox';
import ChatComposer from './components/ChatComposer';
import { useChat } from './hooks/useChat';
import { getHistory } from './api/qa';

export type HistoryItem = { id: string; title: string; last: string };

export default function App() {
  const [question, setQuestion] = useState('');
  const [history, setHistory] = useState<HistoryItem[]>([]);

  const { messages, send, loading } = useChat();

  React.useEffect(() => {
    getHistory().then((h: HistoryItem[]) => setHistory(h));
  }, []);

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
            <div className="fgBrandSub">演示模式（UI 占位）</div>
          </div>
        </div>

        <SideHistory list={history} />

        <div className="fgSideSection">
          <div className="fgSideSectionTitle">提示</div>
          <div className="fgSideHint">
            当前页面已接入问答后端，请先启动 rag-service-node 再测试。
          </div>
        </div>

        <div className="fgSideFooter">
          <div className="fgSideFooterItem">
            <span className="dot online"></span>
            <span>UI：已接真实问答接口</span>
          </div>
        </div>
      </aside>

      <main className="fgMain">
        <ChatHeader
          title="文物知识问答"
          desc="基于 KG + RAG（当前接入规则版问答后端）"
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
