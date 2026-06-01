import { useState } from 'react';

import './styles/app.css';

import ChatHeader from './components/ChatHeader';
import SideHistory from './components/SideHistory';
import ChatBox from './components/ChatBox';
import ChatComposer from './components/ChatComposer';
import { useChat } from './hooks/useChat';

export default function App() {
  const [question, setQuestion] = useState('');

  const {
    conversations,
    activeId,
    activeMessages,
    activeLoading,
    createConversation,
    deleteConversation,
    switchConversation,
    send,
    feedbackState,
    handleFeedback,
  } = useChat();

  async function handleAsk() {
    const q = question.trim();
    if (!q || activeLoading) return;
    await send(q);
    setQuestion('');
  }

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <SideHistory
          conversations={conversations}
          activeId={activeId}
          onSelect={switchConversation}
          onNew={createConversation}
          onDelete={deleteConversation}
        />
      </aside>

      <main className="fgMain">
        <ChatHeader
          title="文物知识问答"
          desc="基于 KG + RAG（Spring后端代理规则版问答服务）"
        />

        <ChatBox messages={activeMessages} loading={activeLoading} onFeedback={handleFeedback} feedbackState={feedbackState} />

        <ChatComposer
          value={question}
          onChange={(v: string) => setQuestion(v)}
          onSend={handleAsk}
          sending={activeLoading}
        />
      </main>
    </div>
  );
}
