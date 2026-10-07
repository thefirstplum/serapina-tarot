# 아키텍처 요약

README에 없는 세부만 적었습니다.

## 컨테이너 구성

```
Docker Compose
  nginx :80/443  ->  backend :8000  ->  mysql :3306
  certbot (12시간마다 renew)
backend  ->  host.docker.internal:11434  ->  Ollama (호스트, GPU)
```

## 동시성

`LLM_MAX_CONCURRENT = 1`인 `asyncio.Semaphore`로 LLM 호출을 직렬화하고 대기 수를 SSE `queue` 이벤트로 보냅니다. 프론트는 "앞에 N명 대기 중" 화면을 띄웁니다. 아무 반응 없이 기다리게 하면 사용자는 고장 난 줄 알고 나갑니다. 세마포어는 프로세스 단위라 uvicorn 워커는 1개로 둡니다. 예전 `--workers 4` 설정에서는 최대 4건이 동시에 들어갔습니다. 클라우드 LLM으로 바꾸면 이 값을 크게 올려도 됩니다.

## RAG

| 단계 | 스크립트 | 하는 일 |
|---|---|---|
| 수집 | `download_tarot_subtitles.py` | 타로 강의 영상 자막 |
| 전처리 | `preprocess_subtitles.py` | 타임스탬프 제거, 문장 재구성, 중복 제거 |
| 정제 | `llm_refine.py` | 구어체 자막을 지식 문서로 |
| 색인 | `build_rag_index.py` | 한국어 임베딩으로 ChromaDB 색인 |

임베딩은 `jhgan/ko-sroberta-multitask`입니다. 다국어 모델보다 한국어 문장 유사도가 나았고 로컬에서 돕니다. `TarotRAGSearch`는 인덱스가 없으면 예외를 던지지만, `main.py`가 그 예외와 검색 실패를 잡고 RAG 없이 리딩을 계속합니다. 예전 유사도 계산 버그(`1 - distance`)가 1년 가까이 드러나지 않은 것도 그래서입니다. 지금은 코사인 유사도를 직접 계산하고, 기동할 때 `selfcheck.py`가 샘플 질문으로 실제 검색 결과가 나오는지 확인합니다.

## 질문 의도와 스프레드

`question_intent.py`가 질문을 선택, 시기, 속마음, 원인, 방법, 가능 여부, 관계, 기간 운세 등으로 나눕니다. 시간 표현("이번 주에")은 조건으로만 보고, 다른 의도가 없을 때만 기간 운세를 고릅니다. 의도가 분명하면 LLM 없이 스프레드를 정하고, 아니면 LLM에 스프레드 이름만 고르게 한 뒤 `spreads.py`의 테이블에서 장수와 위치를 가져옵니다. 타로 자체를 묻는 질문(meta)은 사람 자리가 있는 스프레드를 피합니다.

`card_data.py`의 `build_spread_context()`가 카드마다 주제별 의미, 시기, yes/no 무게를 붙이고, 의료 관련 질문이면 시기 정보를 빼고 전문가 도움을 권하게 합니다.

## 전문가 선택

키워드 매칭(love, career, money, self, daily)으로 먼저 고르고(받침이 붙은 활용형도 잡도록 한글 음절 범위로 매칭), `USE_EMBEDDING_ROUTER=true`일 때만 주제 설명문과의 임베딩 유사도를 봅니다. 둘이 다르면 임베딩 점수가 0.55 이상일 때만 임베딩을 따르고, 둘 다 없으면 `daily`입니다. 임베딩 첫 로드가 17초라 기본은 꺼져 있습니다.

## 보안

- 입력: 주민번호, 계좌번호, 전화번호, 이메일 정규식 마스킹 (`sanitizer.py`)
- 저장: Fernet(AES-128-CBC + HMAC), PBKDF2-HMAC-SHA256 키 유도, 질문과 해석 컬럼 (`encryption.py`). 키가 없으면 서버가 뜨지 않음. salt는 아직 코드에 고정
- 전송: HTTPS, HSTS
- 어드민: Nginx Basic Auth (`/admin`, `/api/admin/*`)
- CORS: 허용 오리진을 환경변수로 명시

## 데이터 모델

MySQL 18개 테이블, `backend/database.py`.

- 핵심: `tarot_sessions`(익명 세션), `tarot_readings`(암호화된 리딩), `daily_usage`(세션별 하루 이용 횟수 기록)
- 피드백: `user_ratings`, `user_contacts`, `user_feedback`(구버전, 보존용)
- 콘텐츠와 광고: `blog_posts`, `ad_impressions`, `ad_clicks`
- 수익화(구현만, 미연결): `users`, `user_auth_sessions`, 포인트 4개, 구독 2개, `rewarded_ad_logs`

## 프론트엔드

Pinia 스토어는 `chatStore`, `authStore`, `pointStore`입니다. `chatStore`가 SSE를 받아 메시지를 조립하고 `queue` 이벤트를 받으면 대기 화면으로 바꿉니다.

핵심 화면은 랜딩과 리딩 둘이고, 나머지 라우트 대부분은 검색 유입용 정적 콘텐츠(카드 상세, 가이드, 블로그, 약관)입니다. SPA는 크롤러에 빈 `<div id="app">`만 보이므로 빌드 후 `scripts/prerender.js`가 puppeteer로 고정 경로 18개, 블로그 글, 카드 상세 30장을 `dist/{path}/index.html`로 렌더하고 Nginx `try_files`가 그 HTML을 먼저 줍니다. 78장을 다 렌더하면 빌드가 너무 길어서 카드는 일부만 합니다. `sitemap.xml`은 백엔드가 DB의 블로그 글까지 넣어 만듭니다.

## 운영

- 배포: `scripts/deploy-simple.sh`가 새 백엔드를 :8001에 띄워 `/health`를 확인한 뒤 :8000으로 교체합니다. 헬스체크에 실패하면 기존 서비스는 그대로 둡니다. 교체하는 사이 몇 초 공백은 남아 있습니다. 자세한 건 [scripts/README.md](../scripts/README.md).
- 인증서: certbot은 제때 갱신했는데 Nginx가 옛 인증서를 메모리에 들고 있어 사이트가 만료로 보인 적이 있습니다. 지금은 `certbot renew --deploy-hook`으로 실제 갱신이 일어났을 때만 Nginx에 SIGHUP을 보냅니다.
- RAG 인덱스는 이미지에 굽지 않고 `docker-compose.yml`에서 마운트합니다. 이미지에 넣었을 때는 인덱스를 갱신해도 컨테이너가 옛 사본을 봤습니다. numpy 2.x에서는 chromadb 0.4.22 import가 실패해 RAG가 조용히 꺼져서 `numpy<2`로 고정했습니다.
- `/admin`은 Nginx Basic Auth(`htpasswd -c nginx/.htpasswd admin`), 인증서는 `nginx/ssl/`에 둡니다.

저장소에 없는 것: RAG 인덱스(약 145MB)와 자막 원본·가공본(약 350MB), 운영 DB 백업과 블로그 콘텐츠 SQL(사용자 데이터 포함), 인증서와 `.env`, 인스타그램 카드뉴스 자동 발행 스크립트.
