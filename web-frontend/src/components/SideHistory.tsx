import React from 'react';

export type HistoryItem = { id: string; title: string; last: string };

export default function SideHistory({ list = [] }: { list?: HistoryItem[] }) {
  return (
    <div className="fgSideSection" style={{ padding: 10 }}>
      <div className="fgSideSectionTitle">会话</div>
      <div className="fgChatList">
        {list.map((it, idx) => (
          <div key={it.id} className={`fgChatListItem ${idx === 0 ? 'active' : ''}`}>
            <div className="fgChatListItemTitle">{it.title}</div>
            <div className="fgChatListItemSub">{it.last}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
