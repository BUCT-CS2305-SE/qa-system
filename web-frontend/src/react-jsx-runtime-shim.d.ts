// 为 tsconfig jsx=react-jsx 提供最小 runtime shim，避免未安装 react 时的编辑器报错。
// 安装真实 react 后可删除。

declare module 'react/jsx-runtime' {
  export const Fragment: any;
  export function jsx(type: any, props: any, key?: any): any;
  export function jsxs(type: any, props: any, key?: any): any;
}
