#!/bin/bash
# 헬스체크 스크립트
# 사용법: ./scripts/healthcheck.sh <service_name_or_url>

SERVICE=$1
MAX_ATTEMPTS=${2:-60}

if [ -z "$SERVICE" ]; then
  echo "사용법: $0 <service_name_or_url> [max_attempts]"
  exit 1
fi

# Docker 컨테이너 헬스체크
if docker ps --format '{{.Names}}' | grep -q "^${SERVICE}$"; then
  echo "Docker 컨테이너 헬스체크: $SERVICE"
  
  for i in $(seq 1 $MAX_ATTEMPTS); do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' $SERVICE 2>/dev/null)
    
    if [ "$STATUS" = "healthy" ]; then
      echo "✅ $SERVICE is healthy"
      exit 0
    fi
    
    echo "⏳ Waiting for $SERVICE to be healthy... ($i/$MAX_ATTEMPTS) [Current: $STATUS]"
    sleep 1
  done
  
  echo "❌ $SERVICE failed health check"
  exit 1
fi

# URL 헬스체크
if [[ $SERVICE == http* ]]; then
  echo "URL 헬스체크: $SERVICE"
  
  for i in $(seq 1 $MAX_ATTEMPTS); do
    if curl -f -s "$SERVICE" > /dev/null 2>&1; then
      echo "✅ $SERVICE is healthy"
      exit 0
    fi
    
    echo "⏳ Waiting for $SERVICE to respond... ($i/$MAX_ATTEMPTS)"
    sleep 1
  done
  
  echo "❌ $SERVICE failed health check"
  exit 1
fi

echo "❌ Unknown service type: $SERVICE"
exit 1
