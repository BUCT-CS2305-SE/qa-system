import type { KeyboardEvent, ChangeEvent } from 'react'

type Props = {
  value: string
  onChange: (v: string) => void
  onSend: () => void
  sending: boolean
}

export default function ChatComposer({ value, onChange, onSend, sending }: Props) {
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
            onChange={(e: ChangeEvent<HTMLTextAreaElement>) => onChange(e.target.value)}
            onKeyDown={(e: KeyboardEvent<HTMLTextAreaElement>) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (!sending && value.trim()) onSend();
              }
            }}
          />
        </div>
        <button className="fgSendBtn" onClick={onSend} disabled={sending}>
          {sending ? '发送中…' : '发送'}
        </button>
      </div>
      <div className="fgComposerHint">提示：Enter 发送 · Shift+Enter 换行</div>
    </footer>
  );
}
