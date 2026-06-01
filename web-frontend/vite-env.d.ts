/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE?: string;
  readonly VITE_AI_API_URL?: string;
  readonly VITE_AI_API_KEY?: string;
  // 需要时在此添加更多 VITE_ 环境变量声明
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
