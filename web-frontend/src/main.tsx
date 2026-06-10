import React from 'react';
import ReactDOM from 'react-dom/client';

import App from './App';

// 从 URL query 参数中提取 token 并存入 localStorage
// Web 端跳转格式: http://<qa-ip>:5173?token=<jwt>
try {
  const params = new URLSearchParams(window.location.search);
  const token = params.get('token');
  if (token) {
    localStorage.setItem('auth_token', token);
    // 清除 URL 中的 token，防止泄露
    const cleanUrl = window.location.origin + window.location.pathname;
    window.history.replaceState({}, document.title, cleanUrl);
  }
} catch {
  // 忽略解析错误，如URL中没有token参数则正常启动
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
