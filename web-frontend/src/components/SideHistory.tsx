
export type ConvItem = {
  id: string;
  title: string;
  lastMessage: string;
  createdAt: number;
};

type Props = {
  conversations: ConvItem[];
  activeId: string;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
};

export default function SideHistory({ conversations, activeId, onSelect, onNew, onDelete }: Props) {
  return (
    <>
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">文</div>
          <div>
            <div className="sidebar-logo-text">文物知识问答</div>
            <div className="sidebar-logo-sub">KG + RAG</div>
          </div>
        </div>

        <button className="sidebar-new-btn" onClick={onNew}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          新建对话
        </button>
      </div>

      <div className="sidebar-body">
        <div className="sidebar-section-title">对话历史</div>
        {conversations.length === 0 ? (
          <div style={{ padding: '12px 6px', fontSize: '12px', color: 'var(--text-muted)' }}>
            暂无对话，点击上方按钮开始
          </div>
        ) : (
          <div className="conv-list">
            {conversations.map((c) => (
              <div
                key={c.id}
                className={`conv-item ${c.id === activeId ? 'active' : ''}`}
                onClick={() => onSelect(c.id)}
              >
                <div className="conv-item-icon">
                  {c.id === activeId ? (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
                    </svg>
                  ) : (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                      <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
                    </svg>
                  )}
                </div>
                <div className="conv-item-body">
                  <div className="conv-item-title">{c.title}</div>
                  <div className="conv-item-time">{formatTime(c.createdAt)}</div>
                </div>
                <button
                  className="conv-item-delete"
                  onClick={(e) => { e.stopPropagation(); onDelete(c.id); }}
                  title="删除对话"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="sidebar-footer">
        <span className="status-dot" />
        Spring + RAG 已连接
      </div>
    </>
  );
}

function formatTime(ts: number): string {
  const d = new Date(ts);
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  if (diff < 60_000) return '刚刚';
  if (diff < 3600_000) return `${Math.floor(diff / 60_000)} 分钟前`;
  if (diff < 86400_000) return `${Math.floor(diff / 3600_000)} 小时前`;
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`;
}
