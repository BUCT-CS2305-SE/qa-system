
export type Msg = { role: 'user' | 'assistant'; text: string; meta?: any };

export default function ChatBox({
  messages = [],
  loading = false,
  onFeedback,
  feedbackState = {},
}: {
  messages?: Msg[];
  loading?: boolean;
  onFeedback?: (idx: number, helpful: boolean) => void;
  feedbackState?: Record<number, 'helpful' | 'unhelpful' | undefined>;
}) {
  return (
    <section className="fgChat" role="log">
      <div className="fgChatInner" style={{ maxWidth: 980, margin: '0 auto' }}>
        {messages.length === 0 ? (
          <div className="fgQuoteDesc center">
            请输入问题开始对话
          </div>
        ) : null}

        {messages.map((m, i) => (
          <div key={i} className={`fgMsgRow ${m.role === 'user' ? 'user' : ''}`}>
            {m.role === 'assistant' ? <div className="fgAvatar bot" /> : null}

            <div className={`fgBubble ${m.role === 'user' ? 'user' : ''}`}>
              <div className="fgBubbleText">{m.text}</div>

              {m.meta?.sources && m.meta.sources.length > 0 && (
                <div className="fgQuoteList">
                  {m.meta.sources.map((s: any, idx: number) => (
                    <div key={idx} className="fgQuoteItem">
                      <div className="fgQuoteTag">doc</div>
                      <div className="fgQuoteBody">
                        <div className="fgQuoteName">{s.source_name}</div>
                        {s.detail_url ? (
                          <a className="fgQuoteDesc" href={s.detail_url} target="_blank" rel="noreferrer">
                            {s.detail_url}
                          </a>
                        ) : (
                          <div className="fgQuoteDesc">无来源链接</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {m.meta?.facts && m.meta.facts.length > 0 && (
                <div className="fgQuoteList">
                  {m.meta.facts.map((fact: any, idx: number) => (
                    <div key={`fact-${idx}`} className="fgQuoteItem">
                      <div className="fgQuoteTag">fact</div>
                      <div className="fgQuoteBody">
                        <div className="fgQuoteName">{fact.key}</div>
                        <div className="fgQuoteDesc">{fact.value}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {m.meta?.llm_note && (
                <div className="fgBubbleMeta" style={{ fontStyle: 'italic' }}>
                  {m.meta.llm_note}
                </div>
              )}

              <div className="fgBubbleMeta">
                <span>{m.role === 'user' ? '你' : '助手'}</span>
                {m.role === 'assistant' && onFeedback && (
                  <span className="fgFeedback">
                    <button
                      className={`fgFeedbackBtn ${feedbackState[i] === 'helpful' ? 'active' : ''}`}
                      title="有帮助"
                      onClick={() => onFeedback(i, true)}
                    >👍</button>
                    <button
                      className={`fgFeedbackBtn ${feedbackState[i] === 'unhelpful' ? 'active' : ''}`}
                      title="不准确"
                      onClick={() => onFeedback(i, false)}
                    >👎</button>
                  </span>
                )}
              </div>
            </div>

            {m.role === 'user' ? <div className="fgAvatar user" /> : null}
          </div>
        ))}

        {loading && (
          <div className="fgMsgRow">
            <div className="fgAvatar bot" />
            <div className="fgBubble">
              <div className="typing-indicator">
                <span /><span /><span />
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
