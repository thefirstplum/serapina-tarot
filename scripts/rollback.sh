#!/bin/bash
# 롤백 스크립트
# 사용법: ./scripts/rollback.sh

set -e

echo "🔄 롤백 시작..."

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. 이전 프론트엔드 복구
echo -e "${YELLOW}📁 이전 프론트엔드 복구 중...${NC}"
if docker exec tarot_nginx test -d /usr/share/nginx/html.old; then
  docker exec tarot_nginx rm -rf /usr/share/nginx/html
  docker exec tarot_nginx mv /usr/share/nginx/html.old /usr/share/nginx/html
  echo -e "${GREEN}✅ 프론트엔드 복구 완료${NC}"
else
  echo -e "${RED}⚠️  백업된 프론트엔드가 없습니다${NC}"
fi

# 2. 백엔드 이미지 확인
echo -e "${YELLOW}🔍 이전 백엔드 이미지 확인 중...${NC}"
if docker images | grep -q "tarot-backend.*previous"; then
  echo -e "${YELLOW}🔄 이전 백엔드로 롤백 중...${NC}"
  
  # 현재 백엔드 중지
  docker stop tarot_backend
  docker rm tarot_backend
  
  # 이전 버전으로 재시작
  docker run -d \
    --name tarot_backend \
    --network ai-tarot-chat_tarot_network \
    -p 8000:8000 \
    --env-file .env \
    --restart unless-stopped \
    tarot-backend:previous
  
  echo -e "${GREEN}✅ 백엔드 롤백 완료${NC}"
else
  echo -e "${YELLOW}⚠️  이전 백엔드 이미지가 없습니다${NC}"
  echo -e "${YELLOW}   현재 백엔드를 재시작합니다${NC}"
  docker restart tarot_backend
fi

# 3. 헬스체크
echo -e "${YELLOW}⏳ 헬스체크 중...${NC}"
sleep 3
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
  echo -e "${GREEN}✅ 롤백 완료 및 헬스체크 성공!${NC}"
else
  echo -e "${RED}❌ 헬스체크 실패!${NC}"
  exit 1
fi
