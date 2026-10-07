import type { Plugin } from 'vite'

// index.html의 %VITE_*% 를 환경변수 값으로 치환하는 플러그인
export function htmlEnvPlugin(): Plugin {
  return {
    name: 'html-env-transform',
    transformIndexHtml(html) {
      return html.replace(/%(\w+)%/g, (match, key) => {
        const value = process.env[key]
        return value !== undefined ? value : match
      })
    }
  }
}
