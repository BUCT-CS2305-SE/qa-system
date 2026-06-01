// Minimal shim for `vite/client` in case the package's distributed types are not found by the TS server.
// This file complements `vite-env.d.ts` and avoids the "找不到 'vite/client' 的类型定义文件" error.

declare module 'vite/client' {
  interface ImportMetaEnv {
    readonly VITE_API_BASE?: string;
    readonly VITE_AI_API_URL?: string;
    readonly VITE_AI_API_KEY?: string;
  }

  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
}
