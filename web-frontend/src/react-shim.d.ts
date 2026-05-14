// 说明：当前 web-frontend 仅用于“样式占位”。
// 如果你还没安装 react/react-dom/@types/react，这里提供最小 shim 以消除 TS/JSX 报错。
// 后续一旦安装真实依赖，可删除本文件。

declare module 'react' {
  export type ReactNode = any;
  export type FC<P = {}> = (props: P) => any;
  export function useState<T>(initialState: T): [T, (v: T) => void];
  export function useMemo<T>(factory: () => T, deps: any[]): T;

  const React: any;
  export default React;
}

declare module 'react-dom/client' {
  export function createRoot(container: Element | DocumentFragment): {
    render(node: any): void;
  };
}

declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}
