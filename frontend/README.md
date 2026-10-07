# frontend

Vue 3 + Vite + TypeScript. 전체 설명은 루트 [README](../README.md)에 있습니다.

```sh
npm install
npm run dev          # 개발 서버
npm run type-check   # vue-tsc
npm run lint         # ESLint (--fix)
npm run build        # 서비스워커 버전 갱신 + 타입 체크 + 빌드
node scripts/prerender.js   # 빌드 후 정적 라우트 HTML 생성
```

`test:unit`(Vitest) 스크립트는 있지만 테스트 파일은 아직 없습니다.
