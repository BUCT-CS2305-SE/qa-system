import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ChatComposer from './ChatComposer'

describe('ChatComposer', () => {
  it('renders textarea and send button', () => {
    render(
      <ChatComposer
        value=""
        onChange={() => {}}
        onSend={() => {}}
        sending={false}
      />
    )
    expect(screen.getByRole('textbox')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /发送/ })).toBeInTheDocument()
  })

  it('disables send button when sending', () => {
    render(
      <ChatComposer
        value="hello"
        onChange={() => {}}
        onSend={() => {}}
        sending={true}
      />
    )
    const btn = screen.getByRole('button', { name: /发送/ })
    expect(btn).toBeDisabled()
  })

  it('displays placeholder text', () => {
    render(
      <ChatComposer
        value=""
        onChange={() => {}}
        onSend={() => {}}
        sending={false}
      />
    )
    expect(screen.getByPlaceholderText(/输入问题/)).toBeInTheDocument()
  })
})
