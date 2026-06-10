# web-frontend — 文物知识问答 Web 前端

基于 React 19 + TypeScript + Vite 8 的问答对话界面，提供自然语言输入、对话展示、来源溯源与反馈交互。

---

## 启动

```powershell
pnpm install
pnpm dev        # http://localhost:5173
```

---

## 功能模块

| 组件 | 文件 | 说明 |
|------|------|------|
| ChatBox | `src/components/ChatBox.tsx` | 对话气泡展示（用户/助手）、sources 可点击链接、facts 列表、反馈按钮 |
| ChatComposer | `src/components/ChatComposer.tsx` | 多行输入框，Enter 发送 / Shift+Enter 换行 |
| ChatHeader | `src/components/ChatHeader.tsx` | 顶部标题栏 + 技术栈标识 |
| SideHistory | `src/components/SideHistory.tsx` | 侧边栏：会话列表（新建/删除/切换）、连接状态 |
| useChat | `src/hooks/useChat.ts` | 会话管理核心：localStorage 持久化（5 天 TTL + 每小时 GC + 上限 500） |
| backendClient | `src/api/backendClient.ts` | API 客户端：ask / feedback / history，超时控制、鉴权透传 |
| 样式系统 | `src/styles/app.css` | 23 个 CSS 变量、暗色/亮色主题、响应式 |

---

## 鉴权配置

系统使用双重鉴权：`X-Api-Key`（内置 `qa-demo-key`）+ `Authorization`（JWT token）。

首次使用需在浏览器 Console 执行设置 JWT token（具体值联系数据组获取）：

```js
localStorage.setItem('auth_token', '<你的JWT>')
```

详见 `USER_MANUAL.md` 2.1.2 节。

---

## 脚本

```powershell
pnpm dev        # 开发模式
pnpm build      # 生产构建（tsc + vite）
pnpm lint       # ESLint 检查
pnpm test       # Vitest 单元测试
pnpm preview    # 预览生产构建
```

---

## 技术栈

- React 19 · TypeScript · Vite 8
- Axios（HTTP 客户端）
- ESLint + Vitest（质量）
- CSS 变量（暗色/亮色）
