FROM python:3.11-slim

# 비root 사용자로 실행
RUN adduser --disabled-password --gecos '' tarotuser

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# requirements만 먼저 복사해서 레이어 캐시 활용
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R tarotuser:tarotuser /app
USER tarotuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# 워커는 1개. LLM 동시 처리 세마포어(_llm_semaphore)가 모듈 전역이라 프로세스마다 따로 생긴다.
# --workers 4였을 때는 "한 번에 1건" 제한이 사실상 4건이 됐고, 동시 요청 2건을 보내도
# 대기 이벤트가 한 번도 안 나갔다(서로 다른 워커로 흩어짐).
# FastAPI는 async라 워커 1개로도 동시 접속은 받고, 무거운 작업은 어차피 GPU 한 곳이다.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]