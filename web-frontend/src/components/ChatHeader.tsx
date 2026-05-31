type Props = {
  title?: string;
  desc?: string;
};

export default function ChatHeader({ title = '问答', desc = '' }: Props) {
  return (
    <header className="fgTopbar">
      <div className="fgTopbarLeft">
        <div className="fgTopbarTitle">{title}</div>
        {desc ? <div className="fgTopbarDesc">{desc}</div> : null}
      </div>
      <div className="fgTopbarRight">
        <div className="fgBadge">Neo4j</div>
        <div className="fgBadge">RAG</div>
      </div>
    </header>
  );
}
