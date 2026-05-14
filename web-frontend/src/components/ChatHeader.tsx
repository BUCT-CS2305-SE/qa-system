import React from 'react';

export type ChatHeaderProps = {
  title?: string;
  desc?: string;
  badges?: string[];
};

export default function ChatHeader({ title = '问答', desc = '', badges = [] }: ChatHeaderProps) {
  return (
    <header className="fgTopbar">
      <div className="fgTopbarLeft">
        <div className="fgTopbarTitle">{title}</div>
        {desc ? <div className="fgTopbarDesc">{desc}</div> : null}
      </div>
      <div className="fgTopbarRight">
        {badges.map((b, i) => (
          <div key={i} className="fgBadge">
            {b}
          </div>
        ))}
      </div>
    </header>
  );
}
