#!/bin/bash
# 간단한 무중단 배포 스크립트
# 사용법: ./scripts/deploy-simple.sh

set -e

echo "🚀 무중단 배포 시작..."

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 프로젝트 루트로 이동
cd "$(dirname "$0")/.."

# 1. 프론트엔드 빌드 (이미 완료되었으므로 스킵)
echo -e "${GREEN}✅ 프론트엔드 빌드 완료 (frontend/dist)${NC}"

# 2. 새 백엔드 이미지 빌드
echo -e "${YELLOW}🔨 백엔드 이미지 빌드 중...${NC}"
docker build -t tarot-backend:new ./backend

# 3. 새 백엔드 컨테이너 시작 (다른 포트)
echo -e "${YELLOW}🚢 새 백엔드 컨테이너 시작 중...${NC}"
docker run -d \
  --name tarot_backend_new \
  --network ai-tarot-chat_tarot_network \
  -p 8001:8000 \
  --env-file .env \
  tarot-backend:new

# 4. 헬스체크 대기 (최대 60초)
echo -e "${YELLOW}⏳ 새 백엔드 헬스체크 중...${NC}"
for i in {1..60}; do
  if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 헬스체크 성공!${NC}"
    break
  fi

  if [ $i -eq 60 ]; then
    echo -e "${RED}❌ 헬스체크 실패! 롤백합니다.${NC}"
    docker stop tarot_backend_new
    docker rm tarot_backend_new
    exit 1
  fi

  echo "대기 중... ($i/60)"
  sleep 1
done

# 5. 이전 백엔드 종료 (docker-compose로 실행된 것이 없으면 스킵)
echo -e "${YELLOW}🛑 이전 백엔드 종료 중...${NC}"
docker stop tarot_backend || true
docker rm tarot_backend || true

# 6. 새 컨테이너를 메인으로 변경
echo -e "${YELLOW}🔀 컨테이너 이름 변경 중...${NC}"
docker stop tarot_backend_new
docker rename tarot_backend_new tarot_backend_temp

# 다시 메인 포트(8000)로 실행
docker run -d \
  --name tarot_backend \
  --network ai-tarot-chat_tarot_network \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  tarot-backend:new

# 임시 컨테이너 제거
docker rm tarot_backend_temp

# 7. 프론트엔드 교체
echo -e "${YELLOW}📁 프론트엔드 파일 교체 중...${NC}"
# 백업
docker exec tarot_nginx sh -c "rm -rf /usr/share/nginx/html.old || true"
docker exec tarot_nginx sh -c "mv /usr/share/nginx/html /usr/share/nginx/html.old || true"
docker exec tarot_nginx mkdir -p /usr/share/nginx/html

# 새 파일 복사
docker cp frontend/dist/. tarot_nginx:/usr/share/nginx/html/

# 8. Nginx 설정 리로드
echo -e "${YELLOW}🔄 Nginx 리로드 중...${NC}"
docker exec tarot_nginx nginx -s reload

# 9. 최종 헬스체크
echo -e "${YELLOW}⏳ 최종 헬스체크 중...${NC}"
sleep 3
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
  echo -e "${GREEN}✅ 최종 헬스체크 성공!${NC}"
else
  echo -e "${RED}❌ 최종 헬스체크 실패!${NC}"
  exit 1
fi

echo -e "${GREEN}✅ 무중단 배포 완료!${NC}"
echo ""
echo "배포 정보:"
echo "- Frontend: 업데이트됨"
echo "- Backend: tarot-backend:new (DuckDuckGo 웹 검색 추가)"
echo "- 이전 버전 백업: /usr/share/nginx/html.old"
