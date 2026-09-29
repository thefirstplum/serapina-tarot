# 세라피나 (Serapina) AI 타로 리딩 서비스

[English](README.en.md) | 한국어

로컬 LLM으로 타로 리딩을 해주는 웹 서비스입니다. 질문 의도에 맞는 스프레드를 고르고, 사용자가 뽑은 카드를 RAG로 찾은 타로 지식과 함께 해석해 SSE로 스트리밍합니다.

운영 중: https://serapina.kr

혼자 만들고 운영하는 개인 프로젝트입니다. 규모는 백엔드 Python 약 1만 700줄(카드 데이터 2천 줄 포함), REST/SSE 엔드포인트 22개, MySQL 테이블 18개, 프론트 Vue SFC 약 20.3k줄(뷰 28개, 컴포넌트 13개)과 TypeScript 약 4.1k줄, 5개 언어입니다.

이 저장소는 비공개 원본에서 비밀정보와 운영 데이터를 빼고 옮긴 사본입니다.

## 기술 스택

- Frontend: Vue 3, TypeScript, Vuetify 3, Pinia, Vite
- Backend: FastAPI, SQLAlchemy 2.0 (async), MySQL 8.0
- AI / 검색: Ollama(로컬 LLM), ChromaDB, sentence-transformers(`jhgan/ko-sroberta-multitask`)
- 인프라: Docker Compose, Nginx, Let's Encrypt(certbot)

## 구조

```
브라우저 --HTTPS--> Nginx (정적 파일, 프리렌더 HTML, /api 프록시)
                       |
                     FastAPI (uvicorn 워커 1개)
                     의도 판정 -> 스프레드 -> 전문가 프롬프트
                     -> RAG 검색 -> LLM 대기열 -> SSE
                       |                          |
                     MySQL (질문/해석 암호화)    Ollama (호스트, GPU)
```

Ollama는 호스트에서 돌립니다. macOS Docker에서는 GPU(Metal)를 못 써서 컨테이너 안에서는 리딩 한 건에 몇 분씩 걸렸습니다. 질문은 LLM에 넘기기 전에 전화번호, 계좌번호 같은 개인정보를 마스킹하고([`sanitizer.py`](backend/sanitizer.py)), DB에는 Fernet으로 암호화해 저장합니다([`encryption.py`](backend/encryption.py)). 세부는 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)에 있습니다.

## 풀었던 문제

GPU 한 대로 동시 요청 받기. 요청이 겹치면 다 같이 느려지다 타임아웃이 나서, 세마포어로 LLM 호출을 한 번에 하나씩 처리하고 대기 인원을 SSE로 보내 "앞에 N명 대기 중"을 띄웁니다. 그런데 대기 화면이 가끔만 떴습니다. uvicorn이 `--workers 4`라 세마포어가 프로세스마다 따로 생겨서 GPU에 4건까지 동시에 들어가고 있었습니다. 워커를 1개로 줄였습니다.

1년 가까이 결과가 0건이던 RAG. 인덱스는 정규화 안 된 L2 거리(80~190)를 주는데 코드는 `1 - distance`로 유사도를 계산해 늘 0이 됐고, 임계값에 전부 걸렸습니다. 검색 실패는 `try/except`가 삼켰고 LLM이 빈자리를 그럴듯하게 메워서 에러도 이상한 출력도 없었습니다. 같은 시기에 마이너 아르카나 56장의 카드 설명이 비어 있던 것도 찾았습니다. 유사도는 코사인으로 직접 계산하게 고쳤고, 기동할 때 카드 데이터, 스프레드 정의, RAG 검색, 암호화를 한 번씩 써 보는 자체 점검([`selfcheck.py`](backend/selfcheck.py))을 넣었습니다.

질문 의도와 시간 표현 구분. "이번 주에 이직 가능할까?"가 주간운세로 빠져 요일별 운세만 늘어놓았습니다. "이번 주에"는 조건이고 "가능할까"가 의도라서, 의도를 먼저 판정해 스프레드를 고르고 시간 표현은 시기 조정에만 쓰게 바꿨습니다([`question_intent.py`](backend/question_intent.py)). 5장 스프레드 답이 중간에 끊기던 건 프롬프트가 약 6,900토큰인데 `num_ctx`가 8192 고정이라서였고, 프롬프트 길이에 맞춰 컨텍스트 크기를 고르게 했습니다.

위기 신호. 10대를 주 대상으로 기획해서 "죽고 싶다" 같은 말이 들어온다고 보고 만들었습니다. 키워드로 다 잡으면 "시험 죽었어"까지 걸려서, 명시적인 표현은 바로 처리하고 애매한 표현만 짧은 분류 프롬프트(`temperature=0`, YES/NO)로 한 번 더 봅니다. 분류 호출이 실패하면 위기로 간주합니다.

배포 후 페이지가 안 넘어가던 문제. API는 200을 주는데 재방문자는 화면이 멈췄습니다. 서비스워커가 `index.html`까지 캐시 우선으로 잡고 있어서 배포 때마다 옛 JS 청크를 요청하고 404를 받았습니다. HTML은 네트워크 우선으로 바꾸고, 청크 로드에 실패하면 캐시를 비우고 한 번 새로고침합니다.

## AI(Claude Code)와 작업한 방식

Claude Code로 만들고 운영했습니다. 원본 저장소 커밋 69개 중 53개가 Claude 공동 작성이고, 51개가 첫 2주에 몰려 있습니다. 그 뒤 반년 가까이 거의 손을 안 댔고, 2026-09에 답변 전문을 읽기 시작하면서 위 문제들이 드러났습니다.

AI는 세션 사이에 기억이 없어서 `CLAUDE.md`에 구조, 명령어, 운영 절차를 두고 매 세션 읽게 했습니다. 2026-07부터는 AI가 세션 끝에 작업 기록을 남기고, 제가 휴대폰에서 코멘트를 달면 다음 세션이 그걸 먼저 반영하게 했습니다. 방향은 대부분 그 코멘트에서 바뀌었습니다. 리딩이 두루뭉술하다고 하자 AI는 말투를 고치려 했는데, 입력을 거슬러 올라가 보니 카드 설명과 RAG 결과가 비어 있었습니다. AI가 만든 깔끔한 질문으로 검증하던 것도 실제 타로 커뮤니티 질문 499개로 바꿨고, 앞의 스프레드 선택과 답 잘림 문제는 그 세트를 돌리다 나왔습니다.

수치를 다시 뽑는 명령과 작업 기록 요약은 [docs/AI-COLLABORATION.md](docs/AI-COLLABORATION.md)에 있습니다.

## 한계

- 자동 회귀 테스트와 CI가 없습니다. 평가 세트는 스크립트로 돌리고 답변은 사람이 읽어서 판단합니다. `backend/test_*.py`는 수동 확인용입니다.
- `main.py`가 약 3,400줄 단일 파일이고, Ollama/Anthropic 전환 코드가 그 안에 흩어져 있습니다. 로깅도 `print`입니다.
- PBKDF2 salt가 코드에 고정돼 있습니다. 위기 분류에서 Ollama가 200이 아닌 응답을 주면 위기 아님으로 떨어지는 경로가 남아 있습니다.
- 결제, 포인트, 카카오 로그인 모듈은 구현만 돼 있고 운영에는 연결하지 않았습니다.
- 9월 수정은 이 사본에는 옮겼지만 비공개 원본에서는 아직 커밋 전입니다.

## 로컬 실행

Node.js 20.19+ 또는 22.12+, Python 3.11+, Docker Compose, 호스트에 설치한 [Ollama](https://ollama.ai)가 필요합니다.

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# ENCRYPTION_PASSWORD, SECRET_KEY, JWT_SECRET_KEY를 임의 값으로 바꾼다

ollama pull gemma3:12b
docker compose up -d mysql

cd backend && pip install -r requirements.txt
uvicorn main:app --reload        # http://localhost:8000/docs

cd ../frontend && npm install
npm run dev                      # http://localhost:5173
```

RAG 인덱스(약 145MB)는 저장소에 없습니다. 없으면 RAG 없이 동작하고, `backend/scripts/`의 파이프라인(자막 수집, 전처리, LLM 정제, 색인)으로 만들 수 있습니다. 배포와 롤백 스크립트는 [scripts/README.md](scripts/README.md)에 정리했습니다.

## 라이선스

코드는 [MIT License](LICENSE)입니다. 카드 이미지는 Rider-Waite 덱(1909, Pamela Colman Smith)으로 퍼블릭 도메인입니다. [ATTRIBUTION.md](ATTRIBUTION.md) 참고.
