export default function ChatComposer({ value, onChange, onSend, sending }: any) {
  return (
    <footer className="fgComposer">
      <div className="fgComposerInner">
        <div className="fgInputWrap">
          <div className="fgInputIcon" aria-hidden="true" />
          <textarea
            className="fgInput"
            placeholder="输入问题（示例：这件文物现在藏在哪个博物馆？）"
            rows={2}
            value={value}
            onChange={(e: any) => onChange(e.target.value)}
          />
        </div>
        <button className="fgSendBtn" onClick={onSend} disabled={sending}>
          {sending ? '发送中…' : '发送'}
        </button>
      </div>
      <div className="fgComposerHint">提示：Ctrl/⌘ + Enter 发送（此处为占位）</div>
    </footer>
  );
}
