# 배포 스크립트

프로젝트 루트에 `.env`가 있어야 합니다.

`deploy-simple.sh`: 프론트는 미리 `npm run build`해 둔 `frontend/dist`를 씁니다. 백엔드 이미지를 `tarot-backend:new`로 빌드해 :8001에 띄우고, `/health`가 200이 될 때까지 최대 60초 기다립니다. 통과하면 구 컨테이너를 내리고 새 이미지를 :8000으로 다시 띄운 뒤, nginx 컨테이너의 정적 파일을 `html.old`로 백업하고 교체한 다음 reload합니다. 구 컨테이너를 내리고 새로 띄우는 사이 몇 초 공백이 있습니다.

`healthcheck.sh`: 컨테이너 이름이나 URL을 받아 healthy/200이 될 때까지 기다립니다. 두 번째 인자는 최대 시도 횟수(기본 60).

```bash
./scripts/healthcheck.sh tarot_backend
./scripts/healthcheck.sh http://localhost:8000 30
```

`rollback.sh`: `html.old`가 있으면 프론트를 되돌리고, `tarot-backend:previous` 이미지가 있으면 백엔드를 그걸로 되돌립니다. `deploy-simple.sh`는 `previous` 태그를 만들지 않으니 백엔드 롤백이 필요하면 배포 전에 직접 태그해 둬야 합니다.

`backup_db.sh`: MySQL 백업.

막혔을 때:

```bash
docker logs tarot_backend_new                 # 헬스체크 실패 원인
lsof -i :8000; lsof -i :8001                  # 포트 충돌
docker stop tarot_backend_new && docker rm tarot_backend_new
docker build --no-cache -t tarot-backend:new ./backend
```

DB 마이그레이션은 아직 수동입니다.
