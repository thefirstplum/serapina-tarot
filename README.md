# Serapina

로컬 LLM 기반 AI 타로 리딩 서비스 | https://serapina.kr

[English](README.en.md) | 한국어

## 개요

외부 API 비용 없이 로컬 LLM만으로 대화형 AI 서비스를 운영할 수 있는지 검증하기 위한 프로젝트. 카드별 해석 체계가 정해져 있는 타로를 도메인으로 선택해, 핵심 해석 지식을 프롬프트와 RAG로 주입하고 LLM이 질문 맥락에 맞는 리딩을 생성하는 구조로 설계. 개발과 운영 모두 1인 진행.

이 저장소는 비공개 원본에서 비밀정보와 운영 데이터를 제외한 공개용 사본.

## 주요 기능

- 질문 의도 분석 기반 스프레드 자동 선택 (시간 표현은 시기 조정에만 반영)
- 카드 해석 지식 RAG 검색 (ChromaDB, ko-sroberta-multitask)
- SSE 스트리밍 응답, GPU 단일 대기열과 대기 순번 표시
- 위기 표현 감지 (명시적 표현은 즉시 처리, 애매한 표현은 분류 프롬프트로 재확인)
- 개인정보 마스킹 후 LLM 전달, 질문과 해석 암호화 저장
- 기동 시 카드 데이터, 스프레드, RAG, 암호화 자체 점검
- 5개 언어 지원

## 아키텍처

```
브라우저 --HTTPS--> Nginx (정적 파일, 프리렌더 HTML, /api 프록시)
                       |
                     FastAPI (uvicorn 워커 1개)
                     의도 판정 -> 스프레드 -> 전문가 프롬프트
                     -> RAG 검색 -> LLM 대기열 -> SSE
                       |                          |
                     MySQL (질문/해석 암호화)    Ollama (호스트, GPU)
```

- LLM: Ollama `qwen3.6:35b-a3b`. 초기 gemma3에서 긴 답변의 일관성과 표현력 문제로 교체
- Ollama는 GPU(Metal) 사용을 위해 Docker 밖 호스트에서 실행
- Claude API 전환 경로 존재. 기본은 Ollama, `AI_PROVIDER=CLAUDE`와 `CLAUDE_API_KEY` 설정 시 전환, 키가 없으면 Ollama로 폴백
- 세부 구조는 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 주요 기술 과제

- 단일 GPU 환경의 동시 요청 처리: 워커 통합과 LLM 호출 직렬화, 대기 순번 SSE 전달
- RAG 유사도 계산 오류 수정과 기동 시 자체 점검 도입
- 질문 의도와 시간 표현을 분리한 스프레드 선택
- 서비스워커 캐시로 인한 배포 후 화면 멈춤 해결
- 타로 커뮤니티 실제 질문 499개 기반 품질 검증

상세 내용은 [docs/NOTES.md](docs/NOTES.md).

## 기술 스택

- Frontend: Vue 3, TypeScript, Vuetify 3, Pinia, Vite
- Backend: FastAPI, SQLAlchemy 2.0 (async), MySQL 8.0
- AI, 검색: Ollama, ChromaDB, sentence-transformers
- 인프라: Docker Compose, Nginx, Let's Encrypt

## 로컬 실행

필요 환경: Node.js 20.19+ 또는 22.12+, Python 3.11+, Docker Compose, 호스트에 설치한 [Ollama](https://ollama.ai)

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# .env 파일의 비밀값(ENCRYPTION_PASSWORD, SECRET_KEY 등)은 임의 값으로 변경

ollama pull qwen3.6:35b-a3b
docker compose up -d mysql

cd backend && pip install -r requirements.txt
uvicorn main:app --reload        # http://localhost:8000/docs

cd ../frontend && npm install
npm run dev                      # http://localhost:5173
```

- RAG 인덱스(약 145MB)는 저장소에 미포함. 인덱스가 없으면 RAG 없이 동작하며, `backend/scripts/` 파이프라인(자막 수집, 전처리, LLM 정제, 색인)으로 생성 가능
- 배포와 롤백 스크립트: [scripts/README.md](scripts/README.md)

## 문서

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) 구조와 데이터 흐름
- [docs/NOTES.md](docs/NOTES.md) 기술 과제와 조치, 향후 개선 과제
- [docs/AI-COLLABORATION.md](docs/AI-COLLABORATION.md) AI 도구 활용과 검증 원칙

## 라이선스

- 코드: [MIT License](LICENSE)
- 카드 이미지: Rider-Waite 덱(1909, Pamela Colman Smith), 퍼블릭 도메인. [ATTRIBUTION.md](ATTRIBUTION.md) 참고
