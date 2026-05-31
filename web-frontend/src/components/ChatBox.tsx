export type Msg = { role: 'user' | 'assistant'; text: string; meta?: any };

export default function ChatBox({ messages = [] }: { messages?: Msg[] }) {
  return (
    <section className="fgChat" role="log">
      <div className="fgChatInner" style={{ maxWidth: 980, margin: '0 auto' }}>
        {messages.length === 0 ? (
          <div className="fgQuoteDesc" style={{ padding: 12 }}>
            请输入问题开始对话
          </div>
        ) : null}

        {messages.map((m, i) => (
          <div key={i} className={`fgMsgRow ${m.role === 'user' ? 'user' : ''}`}>
            {m.role === 'assistant' ? <div className="fgAvatar bot" /> : null}

            <div className={`fgBubble ${m.role === 'user' ? 'user' : ''}`}>
              <div className="fgBubbleText">{m.text}</div>
              {m.meta && m.meta.sources && (
                <div className="fgQuoteList">
                  {m.meta.sources.map((s: any, idx: number) => (
                    <div key={idx} className="fgQuoteItem">
                      <div className="fgQuoteTag">doc</div>
                      <div className="fgQuoteBody">
                        <div className="fgQuoteName">{s.sourceName}</div>
                        <div className="fgQuoteDesc">{s.detailUrl}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="fgBubbleMeta">{m.role === 'user' ? '你' : '助手'}</div>
            </div>

            {m.role === 'user' ? <div className="fgAvatar user" /> : null}
          </div>
        ))}
      </div>
    </section>
  );
}
