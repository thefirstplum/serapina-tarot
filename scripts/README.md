# 배포 스크립트

전제: 프로젝트 루트에 `.env` 필요.

## `deploy-simple.sh`

- 프론트는 사전에 `npm run build`로 생성한 `frontend/dist` 사용
- 백엔드 이미지를 `tarot-backend:new`로 빌드해 :8001에 기동, `/health`가 200이 될 때까지 최대 60초 대기
- 통과 시 구 컨테이너 중지, 새 이미지를 :8000으로 재기동
- nginx 컨테이너의 정적 파일을 `html.old`로 백업 후 교체, reload
- 구 컨테이너 중지와 새 컨테이너 기동 사이 수 초 공백 존재

## `healthcheck.sh`

- 컨테이너 이름 또는 URL을 받아 healthy/200이 될 때까지 대기
- 두 번째 인자는 최대 시도 횟수(기본 60)

```bash
./scripts/healthcheck.sh tarot_backend
./scripts/healthcheck.sh http://localhost:8000 30
```

## `rollback.sh`

- `html.old`가 있으면 프론트 복원
- `tarot-backend:previous` 이미지가 있으면 백엔드 복원
- `deploy-simple.sh`는 `previous` 태그를 생성하지 않으므로 백엔드 롤백이 필요하면 배포 전 수동 태그 필요

## `backup_db.sh`

- MySQL 백업

## 문제 해결

```bash
docker logs tarot_backend_new                 # 헬스체크 실패 원인
lsof -i :8000; lsof -i :8001                  # 포트 충돌
docker stop tarot_backend_new && docker rm tarot_backend_new
docker build --no-cache -t tarot-backend:new ./backend
```

DB 마이그레이션은 아직 수동.
