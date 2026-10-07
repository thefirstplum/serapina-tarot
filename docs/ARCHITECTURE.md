# 아키텍처 요약

README에 없는 세부 사항 정리.

## 컨테이너 구성

```
Docker Compose
  nginx :80/443  ->  backend :8000  ->  mysql :3306
  certbot (12시간마다 renew)
backend  ->  host.docker.internal:11434  ->  Ollama (호스트, GPU)
```

## 동시성

- `LLM_MAX_CONCURRENT = 1`인 `asyncio.Semaphore`로 LLM 호출 직렬화, 대기 수는 SSE `queue` 이벤트로 전달
- 프론트는 `queue` 이벤트 수신 시 "앞에 N명 대기 중" 화면 표시
- 세마포어가 프로세스 단위라 uvicorn 워커 1개로 운영 (`--workers 4`에서는 최대 4건 동시 진입)
- 클라우드 LLM 전환 시 `LLM_MAX_CONCURRENT` 상향 가능

## RAG

| 단계 | 스크립트 | 하는 일 |
|---|---|---|
| 수집 | `download_tarot_subtitles.py` | 타로 강의 영상 자막 |
| 전처리 | `preprocess_subtitles.py` | 타임스탬프 제거, 문장 재구성, 중복 제거 |
| 정제 | `llm_refine.py` | 구어체 자막을 지식 문서로 |
| 색인 | `build_rag_index.py` | 한국어 임베딩으로 ChromaDB 색인 |

- 임베딩: `jhgan/ko-sroberta-multitask`. 다국어 모델 대비 한국어 문장 유사도 우위, 로컬 실행
- `TarotRAGSearch`는 인덱스 부재 시 예외 발생, `main.py`가 예외와 검색 실패를 처리하고 RAG 없이 리딩 진행
- 유사도는 코사인 유사도 직접 계산 (이전 `1 - distance` 방식 대체)
- 기동 시 `selfcheck.py`가 샘플 질문으로 검색 결과 반환 여부 확인

## 질문 의도와 스프레드

- `question_intent.py`가 질문을 선택, 시기, 속마음, 원인, 방법, 가능 여부, 관계, 기간 운세 등으로 분류
- 시간 표현("이번 주에")은 조건으로만 처리, 다른 의도가 없을 때만 기간 운세 선택
- 의도가 명확하면 LLM 없이 스프레드 결정, 불명확하면 LLM이 스프레드 이름만 선택하고 장수와 위치는 `spreads.py` 테이블에서 조회
- 타로 자체에 대한 질문(meta)은 사람 자리가 있는 스프레드 제외
- `card_data.py`의 `build_spread_context()`가 카드별 주제별 의미, 시기, yes/no 가중치 부여
- 의료 관련 질문은 시기 정보 제외, 전문가 도움 권고

## 전문가 선택

- 1차: 키워드 매칭(love, career, money, self, daily). 받침이 붙은 활용형까지 잡도록 한글 음절 범위로 매칭
- 2차: `USE_EMBEDDING_ROUTER=true`일 때만 주제 설명문과의 임베딩 유사도 비교
- 두 결과가 다르면 임베딩 점수 0.55 이상일 때만 임베딩 결과 채택, 둘 다 없으면 `daily`
- 임베딩 첫 로드가 17초라 기본값은 비활성

## 보안

- 입력: 주민번호, 계좌번호, 전화번호, 이메일 정규식 마스킹 (`sanitizer.py`)
- 저장: Fernet(AES-128-CBC + HMAC), PBKDF2-HMAC-SHA256 키 유도, 질문과 해석 컬럼 (`encryption.py`). 키가 없으면 서버 기동 불가. salt는 아직 코드에 고정
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

- Pinia 스토어: `chatStore`, `authStore`, `pointStore`
- `chatStore`가 SSE 수신 후 메시지 조립, `queue` 이벤트 수신 시 대기 화면으로 전환
- 핵심 화면은 랜딩과 리딩 2개, 나머지 라우트 대부분은 검색 유입용 정적 콘텐츠(카드 상세, 가이드, 블로그, 약관)
- SPA는 크롤러에 빈 `<div id="app">`만 노출되므로 빌드 후 `frontend/scripts/prerender.js`가 puppeteer로 고정 경로 18개, 블로그 글, 카드 상세 30장을 `dist/{path}/index.html`로 렌더
- Nginx `try_files`가 프리렌더 HTML 우선 제공
- 78장 전체 렌더 시 빌드 시간이 과도해 카드는 일부만 렌더
- `sitemap.xml`은 백엔드가 DB의 블로그 글까지 포함해 생성

## 운영

- 배포: `scripts/deploy-simple.sh`가 새 백엔드를 :8001에 띄워 `/health` 확인 후 :8000으로 교체. 헬스체크 실패 시 기존 서비스 유지. 교체 중 수 초 공백 존재. 세부는 [scripts/README.md](../scripts/README.md)
- 인증서: Nginx가 갱신 전 인증서를 메모리에 유지하므로 `certbot renew --deploy-hook`으로 실제 갱신 시에만 Nginx에 SIGHUP 전송
- RAG 인덱스: 이미지에 포함하지 않고 `docker-compose.yml`에서 마운트. 이미지 포함 시 인덱스 갱신이 컨테이너에 반영되지 않음
- numpy: 2.x에서 chromadb 0.4.22 import 실패로 RAG가 비활성화되어 `numpy<2` 고정
- `/admin`은 Nginx Basic Auth(`htpasswd -c nginx/.htpasswd admin`), 인증서는 `nginx/ssl/`에 보관

저장소 미포함 항목:

- RAG 인덱스(약 145MB), 자막 원본·가공본(약 350MB)
- 운영 DB 백업, 블로그 콘텐츠 SQL(사용자 데이터 포함)
- 인증서, `.env`
- 인스타그램 카드뉴스 자동 발행 스크립트
