# -*- coding: utf-8 -*-
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import Response
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import httpx
import os
import uuid
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from ollama import Client as OllamaClient
# 한국어 응답 정제기 (mlx 모델 누설 자동 치환)
try:
    from text_refiner import refine as refine_korean, detect_leaks
    REFINER_AVAILABLE = True
except Exception as e:
    print(f"⚠️ text_refiner 로드 실패: {e}")
    REFINER_AVAILABLE = False
    def refine_korean(t): return t
    def detect_leaks(t): return [], []
# Claude API 클라이언트
try:
    from claude_client import call_claude_api, get_claude_model_info, claude_client
    CLAUDE_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Claude API 로드 실패: {e}")
    CLAUDE_AVAILABLE = False
    claude_client = None
# Conditional database import for production deployment
try:
    from database import get_database, create_tables, TarotSession, TarotReading, DailyUsage, AdImpression, AdClick, BlogPost, User, UserAuthSession, PointProduct, PointCost, PointCharge, PointUsage, SubscriptionPlan, SubscriptionPayment, RewardedAdLog, get_kst_today
    DATABASE_AVAILABLE = True
except Exception as e:
    print(f"⚠️ DB 모듈 로드 실패: {e}")
    DATABASE_AVAILABLE = False
    # Create dummy functions when database is not available
    async def get_database():
        return None
    async def create_tables():
        pass
    def get_kst_today():
        from datetime import date
        return date.today()
from dotenv import load_dotenv
try:
    from encryption import get_encryption
    ENCRYPTION_AVAILABLE = True
except Exception as e:
    print(f"⚠️ 암호화 모듈 로드 실패: {e}")
    ENCRYPTION_AVAILABLE = False
    def get_encryption():
        class DummyEncryption:
            def encrypt_text(self, text):
                return text
            def decrypt_text(self, text):
                return text
            def encrypt_json(self, data):
                return json.dumps(data)
            def decrypt_json(self, data):
                return json.loads(data)
        return DummyEncryption()
from card_data import CARD_DESCRIPTIONS, CARD_MAPPING, CARD_DB, build_spread_context
from sanitizer import get_sanitizer
import asyncio
import re
import time
# RAG 시스템
try:
    from rag_search import search_tarot_knowledge, get_rag_search
    RAG_AVAILABLE = True
except Exception as e:
    print(f"⚠️ RAG 시스템 로드 실패: {e}")
    RAG_AVAILABLE = False
    async def search_tarot_knowledge(query: str, n_results: int = 3, format_as_context: bool = True):
        return ""

load_dotenv()

app = FastAPI(
    title="AI Tarot API",
    description="Secure AI-powered tarot reading service",
    version="1.0.0",
    docs_url=None,  # Disable docs in production
    redoc_url=None  # Disable redoc in production
)

# 422 validation 에러 상세 로깅
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"❌ Validation Error on {request.url.path}")
    print(f"❌ Error details: {exc.errors()}")
    try:
        body = await request.body()
        print(f"❌ Request body: {body.decode('utf-8')[:500]}")
    except Exception as e:
        print(f"⚠️ 요청 본문 읽기 실패: {e}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

# CORS
allowed_origins = [
    "https://serapina.kr",
    "https://www.serapina.kr",
    "http://localhost:5173",  # Dev only
    "http://localhost:3000"   # Dev only
]

# Security middleware
allowed_hosts_str = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
allowed_hosts_list = [host.strip() for host in allowed_hosts_str.split(",")]
print(f"[INFO] Allowed hosts: {allowed_hosts_list}")
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts_list
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Accept", "Accept-Language", "Content-Language", "Content-Type"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
    return response

# Pydantic models
class ChatRequest(BaseModel):
    question: str
    cards: list[str]
    conversation_history: list[dict] # e.g., [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    session_id: str = ""
    closing_prompt: str = ""  # 대화 종료 유도 메시지
    context_info: dict = {} # 추가 컴텍스트 정보
    location: dict = {}  # {"latitude": float, "longitude": float, "city": str}
    spread_info: dict = {}  # {"spreadType": str, "cardCount": int, "cardPositions": list[str]}
    use_points: bool = False  # 포인트로 추가 이용
    reading_type: str = "basic"  # basic, premium, special_spread

class ChatResponse(BaseModel):
    answer: str
    session_id: str

class SaveReadingRequest(BaseModel):
    session_id: str
    reading_id: int

class PredictionScoreRequest(BaseModel):
    question: str
    conversation_history: list[dict] = []

class PredictionScoreResponse(BaseModel):
    score: float
    needs_cards: bool
    needs_search: bool
    reasoning: str

class UsageLimitResponse(BaseModel):
    allowed: bool
    remaining_count: int
    reset_time: str
    message: str
    can_use_points: bool = False
    point_balance: int = 0
    extra_reading_cost: int = 20

# 환경 변수, 상수
# AI Provider 선택 (OLLAMA 또는 CLAUDE)
AI_PROVIDER = os.getenv("AI_PROVIDER", "OLLAMA").upper()

# Ollama 설정
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/chat")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
OLLAMA_CLOUD_HOST = os.getenv("OLLAMA_CLOUD_HOST", "")  # https://ollama.com
# 하이브리드 모델: 빠른 작업용 작은 모델, 카드 해석용 큰 모델
OLLAMA_MODEL_LIGHT = os.getenv("OLLAMA_MODEL_LIGHT", "qwen3.6:35b-a3b")  # 질문 분석, 스프레드 선택용
OLLAMA_MODEL_HEAVY = os.getenv("OLLAMA_MODEL_HEAVY", "qwen3.6:35b-a3b")  # 타로 카드 해석용

DAILY_USAGE_LIMIT = 3  # 하루 최대 타로 리딩 횟수
MAX_CONVERSATION_TURNS = 30  # 각 리딩당 최대 대화 턴 수 (사용자+AI 메시지 쌍)

# 동시 LLM 처리 제한
# 로컬 LLM은 GPU 1대라 동시 요청이 몰리면 모두 느려지거나 타임아웃 남.
# 한 번에 LLM_MAX_CONCURRENT 건만 처리하고, 나머지는 대기열에서 순번을 받음.
LLM_MAX_CONCURRENT = 1
_llm_semaphore = asyncio.Semaphore(LLM_MAX_CONCURRENT)
_llm_waiting = 0  # 현재 대기 중인 요청 수 (대기 화면 표시용)

# Ollama Cloud 사용 여부 및 클라이언트 설정
USE_OLLAMA_CLOUD = bool(OLLAMA_API_KEY and OLLAMA_CLOUD_HOST)
OLLAMA_HEADERS = {}
OLLAMA_CLIENT = None

# AI Provider 초기화 상태 출력
print(f"\n{'='*50}")
print(f"🤖 AI Provider: {AI_PROVIDER}")
print(f"{'='*50}")

if AI_PROVIDER == "CLAUDE":
    if CLAUDE_AVAILABLE and claude_client:
        print(f"✅ Claude API 사용")
        model_info = get_claude_model_info()
        print(f"  - Light Model: {model_info['light_model']}")
        print(f"  - Heavy Model: {model_info['heavy_model']}")
    else:
        print(f"⚠️ Claude API가 설정되지 않았습니다. Ollama로 폴백합니다.")
        AI_PROVIDER = "OLLAMA"

if AI_PROVIDER == "OLLAMA":
    if USE_OLLAMA_CLOUD:
        OLLAMA_CLIENT = OllamaClient(
            host=OLLAMA_CLOUD_HOST,
            headers={'Authorization': f'Bearer {OLLAMA_API_KEY}'}
        )
        print(f"✅ Ollama Cloud 사용: {OLLAMA_CLOUD_HOST}")
    else:
        # 로컬 Ollama (httpx 사용)
        OLLAMA_HEADERS = {}
        print(f"ℹ️ 로컬 Ollama 사용: {OLLAMA_API_URL}")
    print(f"  - Light Model: {OLLAMA_MODEL_LIGHT}")
    print(f"  - Heavy Model: {OLLAMA_MODEL_HEAVY}")

print(f"{'='*50}\n")

# 사용량 제한
async def check_daily_usage_limit(session_id: str, db: AsyncSession, user_id: int = None) -> UsageLimitResponse:
    """일일 사용량 제한을 확인하고 결과를 반환. 프리미엄 유저는 무제한."""
    try:
        from sqlalchemy import select

        if user_id:
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if user and user.subscription_tier and user.subscription_expires_at:
                from datetime import timezone, timedelta
                KST = timezone(timedelta(hours=9))
                if user.subscription_expires_at > datetime.now(KST):
                    tomorrow = get_kst_today() + timedelta(days=1)
                    reset_time = f"{tomorrow.strftime('%Y-%m-%d')} 00:00 KST"
                    return UsageLimitResponse(
                        allowed=True,
                        remaining_count=999,
                        reset_time=reset_time,
                        message="프리미엄 회원 - 무제한 이용 가능"
                    )

        today = get_kst_today()
        
        result = await db.execute(
            select(DailyUsage).where(
                DailyUsage.session_id == session_id,
                DailyUsage.usage_date == today
            )
        )
        usage_record = result.scalar_one_or_none()
        
        if usage_record is None:
            # 첫 사용
            remaining = DAILY_USAGE_LIMIT - 1
            message = f"오늘 첫 타로 상담이에요! 하루 {DAILY_USAGE_LIMIT}회까지 이용 가능합니다."
        else:
            remaining = DAILY_USAGE_LIMIT - usage_record.reading_count - 1
            if remaining < 0:
                # 사용량 초과
                from datetime import timedelta
                tomorrow = today + timedelta(days=1)
                reset_time = f"{tomorrow.strftime('%Y-%m-%d')} 00:00 KST"
                return UsageLimitResponse(
                    allowed=False,
                    remaining_count=0,
                    reset_time=reset_time,
                    message=f"오늘의 타로 상담 횟수를 모두 사용했어. 내일 자정에 다시 이용할 수 있어."
                )
            message = f"오늘 {remaining}회 더 이용할 수 있어."
        
        from datetime import timedelta
        tomorrow = today + timedelta(days=1)
        reset_time = f"{tomorrow.strftime('%Y-%m-%d')} 00:00 KST"
        
        return UsageLimitResponse(
            allowed=True,
            remaining_count=max(0, remaining),
            reset_time=reset_time,
            message=message
        )
    except Exception as e:
        # 데이터베이스 오류 시 무제한 허용
        print(f"⚠️ 일일 사용량 조회 실패: {e}")
        from datetime import timedelta
        tomorrow = get_kst_today() + timedelta(days=1)
        reset_time = f"{tomorrow.strftime('%Y-%m-%d')} 00:00 KST"
        return UsageLimitResponse(
            allowed=True,
            remaining_count=999,
            reset_time=reset_time,
            message="데이터베이스 연결 없음 - 무제한 이용 가능"
        )

async def increment_daily_usage(session_id: str, db: AsyncSession):
    """일일 사용량을 1 증가시킴"""
    try:
        from sqlalchemy import select
        
        today = get_kst_today()
        
        result = await db.execute(
            select(DailyUsage).where(
                DailyUsage.session_id == session_id,
                DailyUsage.usage_date == today
            )
        )
        usage_record = result.scalar_one_or_none()
        
        if usage_record is None:
            new_record = DailyUsage(
                session_id=session_id,
                usage_date=today,
                reading_count=1
            )
            db.add(new_record)
        else:
            usage_record.reading_count += 1
            usage_record.updated_at = datetime.now()
        
        await db.commit()
    except Exception as e:
        # 데이터베이스 오류 시 무시
        print(f"⚠️ DB 사용량 기록 실패: {e}")

def clean_chinese(text):
    """2글자 이상 연속 한자(중국어 문장) 제거, 美/韓/日 등 1글자 약칭은 유지"""
    return re.sub(r'[\u4e00-\u9fff]{2,}[，。、；：]*', '', text)

# AI 호출 (Ollama / Claude)
async def call_ai_non_streaming(prompt: str, model_type: str = "light", temperature: float = 0.7, max_tokens: int = 512) -> str:
    """비스트리밍 AI 호출 (질문 분석, 스프레드 선택 등). model_type은 "light" / "heavy"."""
    if AI_PROVIDER == "CLAUDE" and CLAUDE_AVAILABLE:
        # Claude API 사용
        messages = [{"role": "user", "content": prompt}]
        response = await call_claude_api(
            messages=messages,
            system_prompt="You are a helpful AI assistant.",
            model=model_type,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=False
        )
        return response
    else:
        # Ollama 사용
        selected_model = OLLAMA_MODEL_HEAVY if model_type == "heavy" else OLLAMA_MODEL_LIGHT
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(OLLAMA_API_URL, headers=OLLAMA_HEADERS, json={
                "model": selected_model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "think": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            })

            if response.status_code == 200:
                result = response.json()
                return clean_chinese(result['message']['content'])
            else:
                raise Exception(f"AI API 호출 실패: {response.status_code}")

async def classify_crisis_with_llm(text: str) -> bool:
    """Tier 2(애매한 표현)용 위기 분류. YES/NO 한 단어만 받음 (num_predict=5).

    200이 아니면 False, 예외가 나면 위기로 보고 True.
    """
    classify_prompt = f"""너는 위기 신호 판별기야. 다음 사용자 메시지가 자살·자해·삶 포기 같은 본인 위기 표현인지 한 단어로만 답해.

판단 기준:
- 본인이 자기 자신에게 위기 신호(죽고싶다, 사라지고싶다, 안 깨고싶다 등) 표현 → YES
- 일상 비유 ("과제 끝내고 싶어", "시험 죽었어", "치킨 죽음") → NO
- 단순 피로·짜증 ("힘들어", "지쳤어") → NO
- 잠깐 우울 표현인데 죽음·자해 의도 X → NO

메시지: "{text}"

답 (YES 또는 NO 한 단어만):"""

    try:
        selected_model = OLLAMA_MODEL_HEAVY
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(OLLAMA_API_URL, headers=OLLAMA_HEADERS, json={
                "model": selected_model,
                "messages": [{"role": "user", "content": classify_prompt}],
                "stream": False,
                "think": False,
                "options": {"temperature": 0.0, "num_predict": 5}
            })
            if response.status_code == 200:
                result_text = response.json().get('message', {}).get('content', '').strip().upper()
                return result_text.startswith('YES') or result_text.startswith('Y ') or result_text == 'Y'
    except Exception as e:
        print(f"⚠️ 위기 LLM 분류 실패: {e} — 안전 차원에서 위기로 처리")
        return True  # 분류 실패 시 안전하게 위기로 처리 (사용자 보호 우선)
    return False


async def call_ai_streaming(messages: list, system_prompt: str, model_type: str = "heavy", temperature: float = 0.8, max_tokens: int = 2048, force_claude: bool = False):
    """스트리밍 AI 호출. force_claude=True면 AI_PROVIDER와 상관없이 Claude 사용.

    Claude는 문자열 chunk, Ollama는 {"content", "done"} dict를 yield.
    """
    if (force_claude or AI_PROVIDER == "CLAUDE") and CLAUDE_AVAILABLE:
        # Claude API는 messages에 system role을 포함할 수 없음
        # system role 메시지를 제거하고 system_prompt로 합침
        filtered_messages = []
        combined_system = system_prompt

        for msg in messages:
            if msg.get("role") == "system":
                if combined_system:
                    combined_system += "\n\n" + msg.get("content", "")
                else:
                    combined_system = msg.get("content", "")
            else:
                filtered_messages.append(msg)

        # Claude는 대화가 user 메시지로 끝나야 함 (assistant prefill 미지원)
        # 마지막이 assistant면 빈 user 메시지를 붙임
        if filtered_messages and filtered_messages[-1].get("role") == "assistant":
            filtered_messages.append({"role": "user", "content": "계속해줘"})

        # 빈 content 메시지 제거 (Claude API 거부)
        filtered_messages = [m for m in filtered_messages if (m.get("content") or "").strip()]

        # 연속된 동일 role 메시지 병합 (Claude 요구사항)
        merged = []
        for m in filtered_messages:
            if merged and merged[-1].get("role") == m.get("role"):
                merged[-1]["content"] = merged[-1]["content"] + "\n\n" + m.get("content", "")
            else:
                merged.append(dict(m))
        filtered_messages = merged

        # Claude API 스트리밍
        stream_generator = await call_claude_api(
            messages=filtered_messages,
            system_prompt=combined_system,
            model=model_type,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True
        )

        async for chunk in stream_generator:
            yield chunk
    else:
        # Ollama 스트리밍
        selected_model = OLLAMA_MODEL_HEAVY if model_type == "heavy" else OLLAMA_MODEL_LIGHT

        # 컨텍스트는 프롬프트와 생성분을 다 담아야 한다. 8192 고정이던 때 카드 5장 + RAG로
        # 프롬프트가 약 6,900토큰까지 커지자 생성할 자리가 없어 답이 100여 자에서 끊겼다.
        # 한국어는 대략 2자당 1토큰으로 잡고 생성분과 여유 512를 더해 단계별로 고른다.
        _prompt_chars = sum(len(m.get("content") or "") for m in messages)
        _need = int(_prompt_chars / 2) + max_tokens + 512
        _num_ctx = 32768
        for _cap in (8192, 12288, 16384, 24576, 32768):
            if _cap >= _need:
                _num_ctx = _cap
                break
        print(f"⏱️ 프롬프트 {_prompt_chars}자(약 {_prompt_chars//2}t) + 생성 {max_tokens}t, num_ctx={_num_ctx}", flush=True)

        async with httpx.AsyncClient(timeout=180.0) as client:
            async with client.stream(
                "POST",
                OLLAMA_API_URL,
                headers=OLLAMA_HEADERS,
                json={
                    "model": selected_model,
                    "messages": messages,
                    "stream": True,
                    "think": False,
                    "options": {
                        # 공식 권장값(temp 1.0 / top_p 0.95 / top_k 64)은 격식체가 새서
                        # 반말 페르소나 유지하려고 보수적으로 잡음
                        "temperature": temperature,  # 격식체 방지
                        "num_predict": max_tokens,
                        "num_ctx": _num_ctx,
                        "top_p": 0.9,
                        "top_k": 40,
                        "min_p": 0,
                        "repeat_penalty": 1.05,    # looping 방지
                    }
                }
            ) as response:
                response.raise_for_status()

                # 응답을 다 받아서 정제한 뒤 작은 chunk로 나눠 보냄 (fake-streaming)
                # 비스트리밍은 줄바꿈 표시가 깨지고, 스트리밍 중에는 정제를 못 해서 절충
                full_content = ""
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            chunk_data = json.loads(line)
                            if "message" in chunk_data and "content" in chunk_data["message"]:
                                full_content += chunk_data["message"]["content"]
                        except json.JSONDecodeError:
                            continue

                # HTML, 마크다운, 깨진 UTF-8, 영어, 한자, '당신', MBTI 표기 정리
                if REFINER_AVAILABLE and full_content:
                    full_content = refine_korean(full_content)

                # 50자씩 30ms 간격으로 송신
                # 줄바꿈은 chunk에 그대로 포함
                CHUNK_SIZE = 50
                STREAM_DELAY = 0.03
                total_len = len(full_content)
                for i in range(0, total_len, CHUNK_SIZE):
                    chunk_text = full_content[i:i + CHUNK_SIZE]
                    is_last = (i + CHUNK_SIZE) >= total_len
                    yield {"content": chunk_text, "done": is_last}
                    if not is_last:
                        await asyncio.sleep(STREAM_DELAY)

# API endpoints
@app.get("/")
def read_root():
    return {"message": "AI Tarot Backend is running"}

@app.get("/health")
@app.head("/health")
def health_check():
    """프론트 연결 확인용 health check"""
    return {"status": "healthy"}

@app.get("/usage-status/{session_id}", response_model=UsageLimitResponse)
async def get_usage_status(session_id: str, db: AsyncSession = Depends(get_database)):
    """사용자의 일일 사용량 상태를 조회"""
    if db is None:
        # 데이터베이스가 없을 때 기본값 반환
        from datetime import timedelta
        tomorrow = get_kst_today() + timedelta(days=1)
        reset_time = f"{tomorrow.strftime('%Y-%m-%d')} 00:00 KST"
        return UsageLimitResponse(
            allowed=True,
            remaining_count=999,
            reset_time=reset_time,
            message="데이터베이스 연결 없음 - 무제한 이용 가능"
        )
    return await check_daily_usage_limit(session_id, db)

class QuestionClassificationResponse(BaseModel):
    question_type: str  # "tarot", "search", "chat"
    confidence: float  # 0.0-1.0
    reasoning: str
    needs_cards: bool
    needs_search: bool

@app.post("/test/classify_question", response_model=QuestionClassificationResponse)
async def test_classify_question(request: PredictionScoreRequest):
    """[테스트] 질문을 tarot / search / chat 중 하나로 분류"""
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in request.conversation_history])

    classification_prompt = f"""당신은 질문을 분류하는 AI입니다. 사용자의 질문을 다음 3가지 중 하나로 분류하세요:

대화 기록:
{history_str}

사용자 질문: "{request.question}"

분류 기준:

1. **tarot (타로 필요)**
   - 운세 질문: "오늘운세", "연애운", "금전운", "내일운세"
   - 미래 예측: "~될까?", "~갈까?", "~할까?", "어떻게 될까?"
   - 고민/상담: "연애", "취업", "이직", "시험", "진로", "사업"
   - 예: "오늘 운세 어때?", "취업 잘 될까?", "연애운 봐줘"

2. **search (웹 검색 필요)**
   - 실시간 정보: "날씨", "뉴스", "주가", "환율", "시간"
   - 최신 정보: "최신", "요즘", "현재", "지금"
   - 사실 확인: "~이 뭐야?", "~은 누구야?", "~는 어디야?"
   - 예: "오늘 날씨 어때?", "요즘 유행하는 노래", "비트코인 시세"

3. **chat (일반 대화)**
   - 인사: "안녕", "고마워", "잘 가"
   - 후속 질문: 이미 카드를 뽑은 후의 추가 질문
     * "그게 무슨 뜻이야?", "더 자세히", "왜 그런거야?"
     * 대화 기록에 이미 카드 해석이 있다면 대부분 후속 질문
   - 일반 대화: "배고파", "피곤해", "재밌다"

중요: 대화 기록을 잘 보고, 이미 타로 해석을 받은 후라면 새로운 주제가 아닌 한 "chat"으로 분류하세요.

JSON 형식으로만 응답:
{{"question_type": "tarot|search|chat", "confidence": 0.0-1.0, "reasoning": "분류 이유"}}"""

    try:
        ai_response = await call_ai_non_streaming(
            prompt=classification_prompt,
            model_type="light",
            temperature=0.2,
            max_tokens=256
        )

        try:
            parsed = json.loads(ai_response)

            question_type = parsed.get('question_type', 'chat')
            confidence = float(parsed.get('confidence', 0.5))
            reasoning = parsed.get('reasoning', 'AI 분류 완료')

            needs_cards = (question_type == "tarot")
            needs_search = (question_type == "search")

            return QuestionClassificationResponse(
                question_type=question_type,
                confidence=confidence,
                reasoning=reasoning,
                needs_cards=needs_cards,
                needs_search=needs_search
            )
        except json.JSONDecodeError:
            pass
    except Exception as e:
        print(f"❌ 질문 분류 실패: {str(e)}")

    # 폴백: 키워드 기반 분류
    question_lower = request.question.lower()

    if check_needs_web_search(request.question):
        return QuestionClassificationResponse(
            question_type="search",
            confidence=0.7,
            reasoning="키워드 기반 분류: 검색 필요",
            needs_cards=False,
            needs_search=True
        )

    fallback_score = analyze_question_fallback(request.question)
    if fallback_score >= 0.6:
        return QuestionClassificationResponse(
            question_type="tarot",
            confidence=fallback_score,
            reasoning="키워드 기반 분류: 타로 필요",
            needs_cards=True,
            needs_search=False
        )

    return QuestionClassificationResponse(
        question_type="chat",
        confidence=0.6,
        reasoning="키워드 기반 분류: 일반 대화",
        needs_cards=False,
        needs_search=False
    )

@app.post("/analyze_question", response_model=PredictionScoreResponse)
async def analyze_question(request: PredictionScoreRequest):
    """질문에 카드가 필요한 정도를 0~1 점수로 판단"""
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in request.conversation_history])

    prediction_prompt = f"""당신은 타로 상담사야. 사용자 질문이 타로 카드가 필요한지 매우 보수적으로 판단해.

대화 기록:
{history_str}

사용자 질문: "{request.question}"

판단 기준:
1. **타로 카드 필요 (score 0.8-1.0, needs_cards: true)**
   - **명시적인 타로/카드 요청**: "카드 뽑아줘", "타로 봐줘", "점쳐줘" 등
   - **운세 보기 요청**: "운세 봐줘", "오늘 운세 알려줘", "내일 운세 봐줄래?" 등
     * 중요: "봐줘/알려줘/보여줘" + "운세" 조합이면 needs_cards: true
     * 단, "운세가 뭐야?", "아까 운세", "운세 말고" 같은 설명/회상/거부는 false
   - **시점 + 운세 조합**: "오늘 운세", "내일 운세", "이번 주 운세", "3개월 뒤 운세" 등
     * "시간 표현 + 운세" 조합이면 needs_cards: true
   - **미래 시점 질문**: "3개월 뒤 어떨까", "내년에 잘될까", "다음 달 결과는" 등
   - 예시:
     * needs_cards: true → "오늘 운세 봐줘", "타로 봐줄래?", "3개월 뒤 어떨까?"
     * needs_cards: false → "운세가 뭐야?", "아까 본 운세 기억나?", "운세 말고 다른 거"
   - ⚠️ **중요**: 단순히 "~될까?", "~어때?"만으로는 카드 불필요!

2. **카드 불필요 (score 0.0-0.5, needs_cards: false) - 기본값!**
   - **인사/감사**: "안녕", "고마워", "잘 가", "감사"
   - **단순 질문**: "뭐야?", "왜?", "정말?", "어떻게?", "누구?"
   - **일반 대화/고민 상담**: "날씨 좋네", "배고파", "힘들어", "기분 좋아"
   - **설명 요청**: "설명해줘", "알려줘", "뭔데?", "어떤거야?"
   - **후속 질문**: 이미 대화가 진행 중인 모든 경우
     * "그게 무슨 뜻이야?", "더 자세히", "어떤 거지?", "그러면?", "왜 그래?"
     * "~라면?", "~은 어떻게?", "~면 어때?", "그건 뭔데?"
   - **고민/상담 (중요!)**: "취업 고민이야", "연애 시작하려는데", "이직 할까?"
     * → 이런 것들은 대화로 충분히 상담 가능! needs_cards: false
   - **미래 질문**: "~될까?", "~어때?", "~잘될까?" 등
     * → 카드 명시 없으면 대화로 상담! needs_cards: false
   - 예: "취업 잘 될까?", "연애 시작하려는데 어때?", "이직 고민이야"
     * → 모두 needs_cards: false (대화로 충분)

3. **웹 검색 필요 (needs_search: true, needs_cards: false)**
   - 실시간 정보: "날씨", "뉴스", "주가", "환율"
   - 최신 정보: "최신", "요즘", "현재", "지금"

**핵심 원칙 (절대 지킬 것!):**
- **기본값은 항상 needs_cards: false!**
- 카드는 사용자가 **명시적으로 "카드", "타로", "점", "운세"를 요청할 때만** true
- 대화 기록이 1개라도 있으면 → 99% needs_cards: false
- 고민/상담 질문 → needs_cards: false (대화로 충분)
- 미래 예측 질문 → needs_cards: false (대화로 조언 가능)
- **의심스러우면 무조건 needs_cards: false!**

JSON만 출력:
{{"score": 숫자, "needs_cards": true/false, "needs_search": true/false, "reasoning": "이유"}}"""

    try:
        # 질문 분석 (가벼운 옵션)
        ai_response = await call_ai_non_streaming(
            prompt=prediction_prompt,
            model_type="light",
            temperature=0.2,
            max_tokens=128
        )

        try:
            import re
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                import json
                parsed = json.loads(json_match.group())

                score = float(parsed.get('score', 0.5))
                needs_cards = bool(parsed.get('needs_cards', score >= 0.6))
                needs_search = bool(parsed.get('needs_search', score < 0.3))
                reasoning = str(parsed.get('reasoning', 'AI 분석 완료'))

                print(f"🎯 질문: '{request.question}' → needs_cards: {needs_cards}, score: {score}, 이유: {reasoning}")

                return PredictionScoreResponse(
                    score=score,
                    needs_cards=needs_cards,
                    needs_search=needs_search,
                    reasoning=reasoning
                )
        except Exception as e:
            # JSON 파싱 실패 시 폴백
            print(f"⚠️ AI 응답 JSON 파싱 실패: {e}")

    except Exception as e:
        print(f"⚠️ 질문 분석 AI 호출 실패: {e}")

    # 에러 시 기본 폴백 로직
    fallback_score = analyze_question_fallback(request.question)
    needs_cards_fallback = fallback_score >= 0.6
    print(f"⚠️ AI 분석 실패, 폴백 사용 - 질문: '{request.question}' → needs_cards: {needs_cards_fallback}, score: {fallback_score}")
    return PredictionScoreResponse(
        score=fallback_score,
        needs_cards=needs_cards_fallback,
        needs_search=fallback_score < 0.3,
        reasoning="기본 키워드 분석 결과"
    )

async def search_web(query: str, max_results: int = 3, location: dict = None) -> str:
    """웹 검색을 수행하고 결과를 요약 (DuckDuckGo 사용)"""
    try:
        # 위치 정보가 있고 날씨 관련 질문인 경우 위치를 포함해서 검색
        enhanced_query = query
        if location and location.get('city'):
            location_keywords = ['날씨', '기온', '온도', '비', '눈', '태풍', '폭염', '한파', '미세먼지', '황사']
            if any(keyword in query for keyword in location_keywords):
                enhanced_query = f"{location['city']} {query}"

        print(f"🔍 웹 검색 시작: '{enhanced_query}'")

        # DuckDuckGo 검색은 동기라 executor에서 실행
        from duckduckgo_search import DDGS

        search_results = []

        loop = asyncio.get_event_loop()

        def sync_search():
            with DDGS() as ddgs:
                results = list(ddgs.text(enhanced_query, region='kr-kr', max_results=max_results))
                return results

        results = await loop.run_in_executor(None, sync_search)

        for result in results:
            search_results.append({
                'title': result.get('title', '제목 없음'),
                'content': result.get('body', '내용 없음'),
                'url': result.get('href', '')
            })

        if search_results:
            formatted_results = f"'{enhanced_query}' 검색 결과:\n\n"
            for i, result in enumerate(search_results, 1):
                formatted_results += f"{i}. {result['title']}\n"
                formatted_results += f"   {result['content']}\n"
                formatted_results += f"   출처: {result['url']}\n\n"

            print(f"✅ 웹 검색 성공: {len(search_results)}개 결과 반환")
            return formatted_results
        else:
            print(f"⚠️ 웹 검색 결과 없음")
            return f"'{query}'에 대한 검색 결과를 찾을 수 없어."

    except Exception as e:
        print(f"❌ 웹 검색 실패: {str(e)}")
        return f"검색 서비스가 일시적으로 이용할 수 없어."

def check_needs_web_search(question: str) -> bool:
    """최신 정보가 필요한 질문인지 확인"""
    current_info_keywords = [
        '최신', '요즘', '지금', '현재', '오늘', '이번', '새로운', '신규', '최근',
        '뉴스', '소식', '업데이트', '트렌드', '유행', '핫한', '인기',
        '주가', '환율', '코인', '비트코인', '주식', '경제', '증시',
        '날씨', '기온', '온도', '태풍', '폭염', '한파',
        '코로나', '백신', '확진', '감염', '팬데믹',
        '선거', '정치', '대통령', '국회', '정부',
        '2024', '2025', '올해', '내년', '작년'
    ]
    
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in current_info_keywords)

def analyze_question_fallback(question: str) -> float:
    """AI 모델 실패 시 사용할 폴백 로직 (더 엄격한 기준)"""
    # 최신 정보 질문 체크
    if check_needs_web_search(question):
        return 0.1  # 타로보다는 검색이 필요

    # 단순 질문/일상 대화 키워드 (카드 불필요)
    simple_keywords = [
        '안녕', '하이', '날씨', '시간', '배고픈', '졸린', '피곤',
        '뭐야', '왜', '정말', '진짜', '누구', '어디', '언제',
        '설명', '알려줘', '뭔데', '어떤거', '그게', '그건'
    ]
    if any(keyword in question for keyword in simple_keywords):
        return 0.2

    # 명확한 운세 요청만 카드 필요 (엄격한 기준)
    explicit_fortune_keywords = [
        '오늘운세', '내일운세', '이번주운세', '이번달운세', '올해운세',
        '연애운', '금전운', '건강운', '사업운', '취업운', '시험운', '여행운',
        '일일운세', '주간운세', '월간운세', '사주', '관상'
    ]
    if any(keyword in question for keyword in explicit_fortune_keywords):
        return 0.9

    # 미래 시점 + 운세/상황 질문 (포괄적 패턴)
    import re

    # 시간 관련 키워드
    future_time_keywords = [
        '개월', '년', '달', '주', '일',  # 시간 단위
        '내년', '다음해', '올해', '내일', '모레', '글피',  # 특정 시점
        '상반기', '하반기', '분기',  # 기간
        '뒤', '후', '내', '안', '이내',  # 시간 지시어
        '미래', '앞으로', '나중', '다음',  # 미래 표현
    ]

    # 운세/미래 질문 키워드
    fortune_context = [
        # 운세 직접 언급
        '운세', '운', '점', '사주', '궁합', '타로',
        # 미래 질문 표현
        '어때', '어떨까', '어떨지', '어떨거', '어떤지',
        '될까', '될지', '될거', '되나', '되냐',
        '좋을까', '좋을지', '나쁠까', '나쁠지',
        '잘될까', '잘될지', '안될까', '안될지',
        '성공할까', '실패할까', '가능할까',
        # 상황 파악
        '상황', '형편', '처지', '입장',
        '어찌될', '어떻게될', '어케될',
        # 조언/예측 요청
        '알아봐', '봐줘', '예측', '전망', '보여줘',
        '궁금해', '알고싶어', '알려줘',
    ]

    # "3개월 뒤", "1년 후", "개월 내" 등의 패턴 감지
    has_time_reference = any(time in question for time in future_time_keywords)
    has_future_inquiry = any(ctx in question for ctx in fortune_context)

    # 숫자 + 시간단위 패턴도 체크 (예: "3개월", "1년", "2주")
    time_number_pattern = re.search(r'\d+\s*(개월|년|달|주|일)', question)

    if (has_time_reference or time_number_pattern) and has_future_inquiry:
        return 0.85

    # 명확한 미래 예측 표현만 카드 필요
    prediction_patterns = ['될까요', '될까', '될지', '갈까요', '갈까', '할까요', '할까']
    if any(pattern in question for pattern in prediction_patterns):
        return 0.8

    # 구체적인 고민/상담 (명확한 주제가 있을 때만)
    concern_keywords = ['고민이야', '고민인데', '선택해야', '결정해야']
    if any(keyword in question for keyword in concern_keywords):
        return 0.7

    # 짧은 질문은 대부분 후속 질문
    if len(question) <= 10:
        return 0.2
    elif len(question) <= 20:
        return 0.3
    else:
        # 긴 질문이라도 명확한 운세 요청이 아니면 낮은 점수
        return 0.4

# 세션, 리딩 저장
async def get_or_create_session(session_id: str, request: Request, db: AsyncSession):
    """Get existing session or create new one"""
    if db is None:
        # 데이터베이스가 없을 때는 새로운 세션 ID 반환
        return session_id if session_id else str(uuid.uuid4())
        
    try:
        from sqlalchemy import select, text
        
        if session_id:
            result = await db.execute(
                select(TarotSession).where(TarotSession.session_id == session_id)
            )
            session = result.scalar_one_or_none()
            if session:
                return session_id
        
        new_session_id = str(uuid.uuid4())
        user_agent = request.headers.get("user-agent", "unknown")
        
        # 개인정보 암호화 (개인정보 최소 수집 원칙에 따라 IP는 수집하지 않음)
        encryption = get_encryption()
        encrypted_user_agent = encryption.encrypt_text(user_agent)
        
        new_session = TarotSession(
            session_id=new_session_id,
            user_agent=encrypted_user_agent
        )
        
        db.add(new_session)
        await db.commit()
        return new_session_id
    except Exception as e:
        print(f"⚠️ 세션 생성 실패: {e}")
        return session_id if session_id else str(uuid.uuid4())

async def save_reading_to_db(session_id: str, question: str, cards: list, response: str, db: AsyncSession, user_id: int = None):
    """Save tarot reading to database with encryption"""
    if db is None:
        # 데이터베이스가 없을 때는 임의의 ID 반환
        return 1

    try:
        sanitizer = get_sanitizer()

        # 주민번호, 계좌번호, 카드번호 등 심각한 민감정보가 있으면 저장 차단
        should_block_question, block_msg = sanitizer.should_block_save(question)
        should_block_response, _ = sanitizer.should_block_save(response)

        if should_block_question or should_block_response:
            print(f"⚠️ Blocked saving due to sensitive data: {block_msg}")
            return None

        # 전화번호, 이메일 등 민감정보는 마스킹 처리
        sanitized_question, question_modified = sanitizer.sanitize_text(question)
        sanitized_response, response_modified = sanitizer.sanitize_text(response)

        if question_modified or response_modified:
            print(f"ℹ️ Sanitized sensitive data before saving")

        encryption = get_encryption()
        encrypted_question = encryption.encrypt_text(sanitized_question)
        encrypted_cards = encryption.encrypt_json(cards)
        encrypted_response = encryption.encrypt_text(sanitized_response)
        
        reading = TarotReading(
            session_id=session_id,
            user_id=user_id,
            question=encrypted_question,
            selected_cards=encrypted_cards,
            ai_response=encrypted_response
        )
        
        db.add(reading)
        await db.commit()
        await db.refresh(reading)
        return reading.id
    except Exception as e:
        print(f"⚠️ 리딩 저장 실패: {e}")
        return 1

@app.post("/interpret")
async def get_interpretation(
    request: ChatRequest,
    http_request: Request
):
    """질문, 카드, 대화 기록을 받아 해석을 SSE로 스트리밍"""
    start_time = time.time()
    print(f"\n{'='*60}")
    print(f"⏱️ [0.00s] 요청 시작: {request.question[:50]}...")
    print(f"{'='*60}")

    # StreamingResponse가 끝날 때까지 세션을 유지해야 해서 Depends 대신 직접 생성
    from database import AsyncSessionLocal

    db = AsyncSessionLocal()
    print(f"⏱️ [{time.time() - start_time:.2f}s] DB 세션 생성 완료")

    session_id = await get_or_create_session(request.session_id, http_request, db)
    print(f"⏱️ [{time.time() - start_time:.2f}s] 세션 ID 확인 완료: {session_id[:20]}...")

    # 카드가 없을 때만 검색 필요 여부 판단
    search_results = ""
    if not request.cards and request.question:
        print(f"⏱️ [{time.time() - start_time:.2f}s] 웹 검색 필요성 판단 시작")
        try:
            from pydantic import BaseModel
            analysis_request = PredictionScoreRequest(question=request.question)
            analysis_result = await analyze_question(analysis_request)
            print(f"⏱️ [{time.time() - start_time:.2f}s] AI 분석 완료")

            if analysis_result.needs_search:
                search_results = await search_web(request.question, max_results=3, location=request.location)
                print(f"⏱️ [{time.time() - start_time:.2f}s] 웹 검색 완료")
        except Exception as e:
            # 폴백: 키워드 검색
            print(f"⚠️ AI 검색 판단 실패: {e}")
            if check_needs_web_search(request.question):
                search_results = await search_web(request.question, max_results=3, location=request.location)
                print(f"⏱️ [{time.time() - start_time:.2f}s] 웹 검색 완료 (폴백)")
    
    from datetime import datetime
    import pytz
    
    # KST 기준
    kst = pytz.timezone('Asia/Seoul')
    now_kst = datetime.now(kst)
    
    weekdays_ko = {
        'Monday': '월요일',
        'Tuesday': '화요일', 
        'Wednesday': '수요일',
        'Thursday': '목요일',
        'Friday': '금요일',
        'Saturday': '토요일',
        'Sunday': '일요일'
    }
    
    weekday_en = now_kst.strftime('%A')
    weekday_ko = weekdays_ko.get(weekday_en, weekday_en)
    
    current_date_str = f"{now_kst.strftime('%Y년 %m월 %d일')} {weekday_ko}"
    current_time_str = now_kst.strftime('%H시 %M분')
    
    # 페르소나, 톤, 금지어, MBTI 룰은 Modelfile에 있음
    # 여기선 카드/히스토리/질문 조합에 따라 분기만 함
    _is_continuation = bool(request.conversation_history) and not request.cards
    _is_general_chat = not request.conversation_history and not request.cards and bool(request.question)
    try:
        if _is_continuation:
            from prompts import CONTINUATION_PROMPT as system_prompt
        elif _is_general_chat:
            from prompts import GENERAL_CHAT_PROMPT as system_prompt
        else:
            from prompts import SYSTEM_PROMPT as system_prompt
    except ImportError:
        # Fallback (prompts.py 로드 실패 시)
        system_prompt = u"""[현재 시점]
오늘: {current_date} {current_time}

카드 보고 진단·해석만. 행동·시간축·조언은 1단계 전용.
분량은 카드 수에 따라 자연스럽게. 정해진 글자수 없음.

{search_context}{closing_guidance}"""

    closing_guidance = ""
    if request.closing_prompt:
        closing_guidance = f"**중요**: 이번 응답 마지막에 다음 멘트를 자연스럽게 포함해서 대화를 마무리 방향으로 유도하세요: \"{request.closing_prompt}\""
    
    search_context = ""
    if search_results:
        search_context = f"""
**최신 정보 참고:**
사용자가 최신 정보를 요청했으므로 다음 검색 결과를 참고해서 답변해주세요:

{search_results}

위 검색 결과를 바탕으로 정확하고 최신의 정보를 제공하되, 세라피나의 따뜻하고 솔직한 톤을 유지해줘.
검색 결과가 불확실하거나 부족하다면 그 점도 솔직히 말해줘."""
    
    # context_info 반영
    context_guidance = ""
    if hasattr(request, 'context_info') and request.context_info:
        context_parts = []

        # 첫 방문 여부 확인
        if request.context_info.get('is_first_visit'):
            context_parts.append("이건 사용자와의 첫 만남이야. 친근하게 인사하고 편하게 대화를 시작해줘.")

        if request.context_info.get('conversation_depth') == 'deep':
            context_parts.append("이 사용자는 이미 긴 대화를 나누고 있으므로 더 깊고 맞춤화된 조언을 원할 수 있어.")

        if request.context_info.get('has_previous_readings'):
            context_parts.append("이전에도 카드 해석을 받았으므로 연속성을 고려한 상담이 도움이 될 거야.")

        # MBTI 컨텍스트 (사용자가 선택한 경우만)
        mbti = request.context_info.get('mbti')
        if mbti:
            try:
                from prompts import get_mbti_context
                mbti_ctx = get_mbti_context(mbti)
                if mbti_ctx:
                    context_parts.append(mbti_ctx)
            except Exception as e:
                print(f"⚠️ MBTI 컨텍스트 처리 실패: {e}")

        # follow-up 깊이 ('더 깊게' 누른 횟수)
        followup_depth = request.context_info.get('followup_depth', 0)
        if followup_depth and int(followup_depth) > 0:
            try:
                from prompts import get_followup_depth_guide
                depth_guide = get_followup_depth_guide(followup_depth)
                if depth_guide:
                    context_parts.append(depth_guide)
                    print(f"⏱️ Follow-up depth {followup_depth} 가이드 주입")

                # 이전 응답 요약. 모델이 앞에서 한 말을 반복하지 않게
                prev_assistants = [m for m in request.conversation_history if m.get('role') == 'assistant']
                if prev_assistants:
                    summaries = []
                    for i, msg in enumerate(prev_assistants, 1):
                        content = (msg.get('content') or '').strip()
                        # 앞 80자 + 뒤 60자
                        if len(content) > 160:
                            short = content[:80].strip() + ' ... ' + content[-60:].strip()
                        else:
                            short = content
                        if i == 1:
                            summaries.append(f"[첫 카드 해석 요약] {short}")
                        else:
                            summaries.append(f"[이전 깊이 {i-1}단계 요약] {short}")

                    # 다음 단계 번호
                    next_n = followup_depth
                    summary_block = (
                        f"🚨 지금부터 너는 {next_n}번째 응답을 작성하는 거야 — 이전 응답들은 다 끝났어:\n\n"
                        + "\n\n".join(summaries)
                        + f"\n\n→ 위 응답들에 나온 단어·문장 구조·비유는 **절대** 다시 사용하지 마.\n"
                        f"→ {next_n}번째 응답이니까 — 시그니처대로 시작해서 — 완전히 새로운 각도로만 답해.\n"
                        f"→ 만약 위 응답에서 '달 카드는 무의식이다'라고 말했으면, 이번엔 그 단어 빼고 다른 표현으로.\n"
                    )
                    context_parts.append(summary_block)
                    print(f"⏱️ 이전 응답 {len(prev_assistants)}개 요약 시그널 주입 (다음: {next_n}번째)")
            except Exception as e:
                print(f"⚠️ Follow-up 깊이 가이드 처리 실패: {e}")

        if context_parts:
            context_guidance = f"\n\n**사용자 컴텍스트 정보:**\n" + "\n".join(context_parts)
    
    # Follow-up이면 첫 응답용 긴 시스템 프롬프트 대신 follow-up 전용 짧은 프롬프트 사용
    # (긴 프롬프트는 첫 응답 가이드가 너무 강해 depth 가이드를 모델이 무시함)
    _followup_depth = int(request.context_info.get('followup_depth', 0) or 0)
    # 도입부가 매번 같지 않게 시간 기반 시드로 셔플
    try:
        from prompts import get_shuffled_intros
        _intro_seed = int(time.time() * 1000) % 1000000
        _shuffled_intros = get_shuffled_intros(seed=_intro_seed, n=6)
    except ImportError:
        _shuffled_intros = '- "오늘은 [카드] 카드가 나왔어."'

    if _followup_depth > 0:
        try:
            from prompts import FOLLOWUP_SYSTEM_PROMPT
            final_system_prompt = FOLLOWUP_SYSTEM_PROMPT + context_guidance
            print(f"⏱️ Follow-up 전용 시스템 프롬프트 적용 (depth={_followup_depth})")
        except ImportError:
            final_system_prompt = system_prompt
    elif _is_continuation or _is_general_chat:
        # CONTINUATION/GENERAL_CHAT은 format 토큰 없음, 그대로 사용
        final_system_prompt = system_prompt + ('\n\n' + context_guidance if context_guidance else '')
        print(f"⏱️ {'CONTINUATION' if _is_continuation else 'GENERAL_CHAT'} 모드 적용")
    else:
        final_system_prompt = system_prompt.format(
            current_date=current_date_str,
            current_time=current_time_str,
            closing_guidance=closing_guidance,
            search_context=search_context + context_guidance,
            shuffled_intros=_shuffled_intros,
        )

    if request.reading_type == "premium" and request.cards:
        try:
            from prompts import PREMIUM_READING_PROMPT
            final_system_prompt += "\n\n" + PREMIUM_READING_PROMPT
        except ImportError:
            pass

    # Mini-MoE: 질문 도메인에 맞는 expert 프롬프트 추가
    # 고른 도메인은 아래 카드 컨텍스트 조립에서도 쓴다
    _expert_id = None
    try:
        from experts import get_expert, build_expert_system, EXPERT_LABELS
        _user_q = request.question or ''
        if not _user_q and request.conversation_history:
            for _msg in reversed(request.conversation_history):
                if _msg.get('role') == 'user' and _msg.get('content'):
                    _user_q = _msg.get('content')
                    break
        if _user_q:
            _expert_id = get_expert(_user_q)
            _expert_prompt = build_expert_system(_expert_id)
            final_system_prompt += "\n\n" + _expert_prompt
            print(f"⏱️ Mini-MoE expert 선택: {EXPERT_LABELS.get(_expert_id, _expert_id)} ({_expert_id})")
    except ImportError as _e:
        print(f"⚠️ Mini-MoE 로드 실패: {_e}")
    except Exception as _e:
        print(f"⚠️ Mini-MoE 처리 실패: {_e}")

    messages = [{"role": "system", "content": final_system_prompt}]

    # 대화 턴 수 체크 (사용자 메시지만 카운트)
    user_message_count = sum(1 for msg in request.conversation_history if msg.get('role') == 'user')
    if user_message_count >= MAX_CONVERSATION_TURNS:
        async def turn_limit_response():
            yield f"data: {json.dumps({'content': '이번 타로 리딩은 여기까지! 💫'})}\n\n"
            yield f"data: {json.dumps({'content': ' 오늘 나눈 이야기가 도움이 되었길 바라. 새로운 고민이 생기면 언제든 다시 찾아와줘! 🌙'})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(turn_limit_response(), media_type="text/event-stream")

    sanitizer = get_sanitizer()
    sanitized_history = []

    for msg in request.conversation_history:
        should_block, block_msg = sanitizer.should_block_save(msg.get('content', ''))
        if should_block:
            # 심각한 민감정보가 있으면 경고 메시지로 대체
            sanitized_msg = {
                "role": msg.get('role'),
                "content": "[민감한 개인정보가 포함되어 저장할 수 없습니다]"
            }
            sanitized_history.append(sanitized_msg)
            print(f"⚠️ Blocked message with sensitive data: {block_msg}")
        else:
            # 일반 민감정보는 마스킹 처리
            sanitized_content, _ = sanitizer.sanitize_text(msg.get('content', ''))
            sanitized_msg = {
                "role": msg.get('role'),
                "content": sanitized_content
            }
            sanitized_history.append(sanitized_msg)

    # History 압축 (rolling summary)
    # 직전 assistant 1개는 원문 유지, 그 이전은 한 줄 요약
    # [이전 응답: ...] 같은 메타 괄호는 빼야 모델이 자기 발화로 인식함
    _fd_history = int(request.context_info.get('followup_depth', 0) or 0)
    if len(sanitized_history) > 0:
        # 마지막 assistant 인덱스 (원문 유지)
        last_assistant_idx = -1
        for i in range(len(sanitized_history) - 1, -1, -1):
            if sanitized_history[i].get('role') == 'assistant':
                last_assistant_idx = i
                break

        compressed_history = []
        for i, msg in enumerate(sanitized_history):
            if msg.get('role') == 'assistant' and i != last_assistant_idx:
                # 그 외 assistant 응답은 첫 50자만
                content = msg.get('content', '') or ''
                summary = content[:80].strip().split('\n')[0]
                if len(content) > 80:
                    summary = summary + '...'
                compressed_history.append({"role": "assistant", "content": summary})
            else:
                compressed_history.append(msg)
        sanitized_history = compressed_history
        if last_assistant_idx >= 0:
            print(f"⏱️ History 압축 — 직전 assistant verbatim, 그 이전 요약 (depth={_fd_history})")

    # Add sanitized messages from the frontend.
    messages.extend(sanitized_history)

    # 현재 질문도 민감정보 체크
    should_block_question, block_msg = sanitizer.should_block_save(request.question)
    if should_block_question:
        # 심각한 민감정보가 있으면 경고 응답 반환
        async def error_response():
            yield f"data: {json.dumps({'content': block_msg})}\n\n"
            yield f"data: {json.dumps({'content': ' 개인정보는 입력하지 말아줘! 🙏'})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(error_response(), media_type="text/event-stream")

    sanitized_question, _ = sanitizer.sanitize_text(request.question)

    # If this is the very first call (history is empty AND no cards AND no question), it's a greeting request.
    # Cards check is done AFTER this, so card interpretation takes priority.
    # 질문이 있으면 인사말이 아니라 일반 대화로 처리
    if not request.conversation_history and not request.cards and not request.question:
        # AI가 상황에 맞는 다양한 인사말을 직접 생성하도록 지시
        import random
        from datetime import datetime
        
        # 시간대 (KST)
        current_hour = now_kst.hour
        time_context = ""
        if 5 <= current_hour < 12:
            time_context = "좋은 아침"
        elif 12 <= current_hour < 18:
            time_context = "좋은 오후"
        elif 18 <= current_hour < 22:
            time_context = "좋은 저녁"
        elif 22 <= current_hour < 24:
            time_context = "늦은 밤"
        else:  # 0 <= current_hour < 5
            time_context = "이른 새벽"
        
        # 계절 (KST)
        current_month = now_kst.month
        season_context = ""
        if current_month in [3, 4, 5]:
            season_context = "봄"
        elif current_month in [6, 7, 8]:
            season_context = "여름"
        elif current_month in [9, 10, 11]:
            season_context = "가을"
        else:
            season_context = "겨울"
        
        # 요일 (KST)
        weekday = now_kst.weekday()
        day_contexts = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
        day_context = day_contexts[weekday]
        
        greeting_prompt = f"""지금 시간은 {time_context}, 요일은 {day_context}, 계절은 {season_context}이야.
        처음 만나는 사용자에게 세라피나(타로 상담사)로서 친구처럼 편하게 반말로 인사해줘.

        🚨 절대 지켜야 할 규칙:
        - 100% 한국어로만! 일본어, 영어 등 외국어 절대 금지!
        - "~능", "~데스" 같은 일본어 말투 절대 사용 금지!
        - 순수 한국 10대 친구 말투로만 ("~야", "~어", "~지?", "~네", "~다")

        🚨 인사말 절대 금지 표현:
        - ❌ "가을 일요일 오후네", "겨울 평일 저녁이네" 같이 계절+요일+시간대를 나열하는 것 금지!
        - ❌ 시간/요일/계절을 한 문장에 모두 언급하지 마!

        인사말 올바른 방법:
        1. **가장 좋은 방법**: 시간/날짜 언급 없이 간단하게
           - "안녕!", "반가워!", "뭐 궁금한 거 있어?", "무슨 일 있었어?"

        2. **시간대만 자연스럽게** (아침: "일찍 일어났네?", 저녁: "저녁 먹었어?", 밤: "이 시간까지 안 자?")

        3. **요일만 자연스럽게** (주말: "주말인데 뭐 해?", 평일: "학교 어땠어?")

        - 매번 다른 느낌의 인사말 (공식적이지 않고 친근하게)
        - 10대 친구가 말하는 것처럼 자연스럽고 따뜻하게
        - 2-3문장 정도로 간결하게

        좋은 예시:
        - "안녕~ 오늘 하루 어땠어?"
        - "반가워! 뭔가 고민 있어? 편하게 말해봐."
        - "저녁 먹었어? 오늘 무슨 일 있었어?"
        - "안녕! 타로 궁금한 거 있어?"
        - "이 시간까지 안 자? 무슨 고민 있어?"

        나쁜 예시 (절대 사용 금지):
        - "가을 일요일 오후네" (계절+요일+시간대 나열)
        - "こんにちは" (일본어)
        - "안녕하세요능~" (~능 말투)

        위는 예시일 뿐이니 매번 새롭고 자연스러운 한국어 인사를 만들어줘."""
        
        selected_greeting = greeting_prompt
        messages.append({"role": "user", "content": selected_greeting})
    # If cards are provided, the user's question is the last message in the history.
    # We add a final system instruction to ensure the AI interprets the cards.
    elif request.cards:

        # RAG: 질문 관련 타로 지식 검색
        rag_context = ""
        if RAG_AVAILABLE:
            try:
                print(f"⏱️ [{time.time() - start_time:.2f}s] RAG 검색 시작")
                rag_context = await search_tarot_knowledge(sanitized_question, n_results=3)
                if rag_context:
                    print(f"⏱️ [{time.time() - start_time:.2f}s] ✅ RAG 컨텍스트 추가됨 ({len(rag_context)} chars)")
                else:
                    print(f"⏱️ [{time.time() - start_time:.2f}s] ℹ️ RAG 검색 결과 없음")
            except Exception as e:
                print(f"⏱️ [{time.time() - start_time:.2f}s] ⚠️ RAG 검색 실패 (해석 계속 진행): {e}")
                rag_context = ""
        # Use imported card mapping that includes reversed cards
        
        card_names = []
        for card in request.cards:
            card_name = CARD_MAPPING.get(card, None)
            if card_name is None:
                # 매핑되지 않은 카드 처리
                print(f"⚠️  WARNING - 매핑되지 않은 카드: '{card}'")
                card_name = f"Unknown Card ({card})"
            card_names.append(card_name)
        
        # Add visual descriptions for better interpretation
        card_details = []
        card_descriptions = CARD_DESCRIPTIONS
        spread_info = request.spread_info
        card_positions = spread_info.get('cardPositions', []) if spread_info else []
        spread_type = spread_info.get('spreadType', '') if spread_info else ''

        for idx, card in enumerate(request.cards):
            card_name = CARD_MAPPING.get(card, None)
            if card_name is None:
                print(f"⚠️  WARNING - 매핑되지 않은 카드: '{card}'")
                card_name = f"Unknown Card ({card})"

            # 1단계(행동 가이드)에서는 카드 의미를 다시 풀지 않아서 카드명만 쓴다
            if idx < len(card_positions) and card_positions[idx]:
                card_details.append(f"[{card_positions[idx]}] {card_name}")
            else:
                card_details.append(card_name)

        # 0단계용 카드 컨텍스트. 질문 유형별 의미, 시기, yes/no를 넣는다.
        # 예전에는 카드 이름과 그림 묘사 한 줄만 들어가서(마이너 56장은 그마저 비어 있었다)
        # 모델이 키워드만 풀어 쓰고 누구에게나 비슷한 리딩이 나왔다.
        # 질문 의도에 따라 무엇에 답해야 하는지도 같이 붙인다.
        _intent_duty = ""
        try:
            from question_intent import detect_intent, answer_duty
            _qi = detect_intent(sanitized_question)
            _duty = answer_duty(_qi["intent"])
            if _duty:
                _intent_duty = f"\n\n[이 질문이 요구하는 답. 반드시 지킬 것]\n{_duty}"
            print(f"⏱️ 질문 의도: {_qi['intent']} ({_qi['reason']})")
        except Exception as _e:
            print(f"⚠️ 의도 판정 실패: {_e}")

        try:
            card_context_block = build_spread_context(
                request.cards, topic=_expert_id, positions=card_positions,
                question=sanitized_question, spread_type=spread_type
            ) + _intent_duty
        except Exception as _e:
            print(f"⚠️ 카드 컨텍스트 조립 실패, 카드명만 사용: {_e}")
            card_context_block = ', '.join(card_details)

        # 스프레드 정보를 포함한 해석 가이드
        spread_context = ""
        if spread_type and card_positions:
            position_guide = "\n".join([f"  - {i+1}번째 카드 ({card_positions[i]}): {card_names[i] if i < len(card_names) else '알 수 없음'}" for i in range(len(card_positions))])

            # 스프레드별 상세 가이드
            spread_guides = {
                "일일운세": """
**해석 가이드 (일일운세):**
⚠️ 중요: 사용자가 질문에서 언급한 날짜 (오늘/내일/모레)를 정확히 지켜서 해석해!
- 1번째 위치가 "오늘"이면 → "오늘은..."
- 1번째 위치가 "내일"이면 → "내일은..."
- 1번째 위치가 "모레"이면 → "모레는..."
각 날짜별로 어떤 일이 있을지, 주의할 점은 무엇인지 해석해줘.""",

                "주간운세": """
**해석 가이드 (주간운세):**
⚠️ 중요: 카드 위치 라벨을 정확히 따라야 해!
- 1번째 카드: 위치 라벨에 명시된 시기 (예: "주초", "남은 주중", "오늘 토요일")
- 2번째 카드: 위치 라벨에 명시된 시기 (예: "주중", "주말", "내일 일요일")
- 3번째 카드: 위치 라벨에 명시된 시기 (예: "주말", "다음 주 시작", "다음 주 월요일")
**절대 위치 라벨을 무시하고 임의로 "이번주/다음주/전말" 같은 말을 하면 안 돼!**
각 시기에 어떤 흐름이 있을지, 주의할 점은 무엇인지 해석해줘.""",

                "월간운세": """
**해석 가이드 (월간운세):**
1. 이번 달 전체운 → 이번 달의 전반적인 흐름
2. 연애/관계운 → 사람 관계나 연애 운세
3. 학업/진로운 → 공부나 진로, 일에 관한 운세
4. 주의할 점 → 조심해야 할 것
5. 조언 → 이번 달을 잘 보내기 위한 조언""",

                "연간운세": """
**해석 가이드 (연간운세):**
1. 상반기 → 올해 전반부 (1월~6월) 흐름
2. 하반기 → 올해 후반부 (7월~12월) 흐름
3. 중요한 기회 → 놓치지 말아야 할 기회
4. 주의할 점 → 조심해야 할 것
5. 올해 조언 → 올해를 잘 보내기 위한 전반적 조언""",

                "짝사랑운세": """
**해석 가이드 (짝사랑운세):**
1. 내 마음 상태 → 지금 내 감정이 어떤지
2. 상대방 마음 → 상대가 나를 어떻게 생각하는지
3. 다가갈 방법 → 구체적으로 어떻게 다가가면 좋을지
4. 앞으로 전망 → 이 짝사랑이 어떻게 될지""",

                "썸운세": """
**해석 가이드 (썸운세):**
1. 현재 썸 상황 → 지금 우리 사이가 어떤 상태인지
2. 상대 진심도 → 상대가 나한테 진심인지, 얼마나 관심 있는지
3. 발전 가능성 → 이 썸이 연애로 발전할 수 있는지
4. 조언 → 이 썸에서 내가 취해야 할 태도""",

                "사귀는중운세": """
**해석 가이드 (사귀는중운세):**
1. 우리 관계 → 지금 우리 관계의 상태와 분위기
2. 상대방 마음 → 남친/여친의 진짜 마음
3. 주의할 점 → 조심해야 할 것, 갈등 요소
4. 앞으로 → 우리 관계가 앞으로 어떻게 될지""",

                "이별/재회운세": """
**해석 가이드 (이별/재회운세):**
1. 현재 상대 마음 → 지금 상대가 나를 어떻게 생각하는지
2. 재회 가능성 → 다시 만날 수 있을지, 가능성은 얼마나 되는지
3. 나아갈 방향 → 내가 지금 어떻게 하면 좋을지""",

                "소개팅/만남운세": """
**해석 가이드 (소개팅/만남운세):**
⚠️ 중요: 이 질문은 "아직 남자친구/여자친구가 없는 상황"에서 새로운 만남을 기대하는 질문이야!
1. 만남 가능성 → 새로운 연인을 만날 가능성이 얼마나 되는지
2. 좋은 인연 시기 → 언제쯤 좋은 사람 만날 수 있을지 (구체적인 시기 언급)
3. 주의사항 → 만남을 위해 조심하거나 준비해야 할 점""",

                "연애운세": """
**해석 가이드 (연애운세):**
1. 현재 상황 → 지금 연애 운의 전반적 상태
2. 상대방 마음 → 관심 있는 사람이나 연인의 마음
3. 관계 발전 → 앞으로 관계가 어떻게 발전할지
4. 해결해야 할 문제 → 풀어야 할 문제나 장애물
5. 최종 결과 → 결국 어떻게 될지""",

                "우정/친구운세": """
**해석 가이드 (우정/친구운세):**
1. 현재 관계 → 지금 친구 관계 상태
2. 주의할 점 → 조심해야 할 것
3. 더 좋아지려면 → 관계 개선 방법""",

                "학업운세": """
**해석 가이드 (학업운세):**
1. 현재 학습 상태 → 지금 공부 상태와 집중도
2. 집중해야 할 부분 → 어디에 신경 써야 하는지
3. 시험 결과 전망 → 시험이나 성적이 어떨지"""
            }

            spread_guide = spread_guides.get(spread_type, "")

            spread_context = f"""
**스프레드 정보: {spread_type}**
{position_guide}
{spread_guide}

**중요: 각 카드를 반드시 해당 위치의 의미에 맞춰 해석해야 해!**
예를 들어 "상대방 마음" 위치의 카드는 상대의 감정과 생각을 중심으로 해석하고,
"앞으로 전망" 위치의 카드는 미래 흐름을 중심으로 해석해줘."""

        # RAG 지식 추가
        rag_knowledge_text = ""
        if rag_context:
            rag_knowledge_text = f"""

**타로 전문 지식 참고:**
다음은 유사한 질문/상황에 대한 타로 해석 사례야. 참고만 하되, 네 스타일로 자연스럽게 풀어서 해석해줘:

{rag_context}

⚠️ **중요**: 위 참고 자료에서 "언젠가", "조만간", "곧", "긍정적으로 생각해" 같은 애매한 표현은 절대 사용하지 마!
반드시 구체적인 시기("2-3개월", "이번 달 안에")와 행동("매일 30분씩 운동", "친구한테 먼저 연락")으로 바꿔서 말해줘!"""

        # 카드 장수에 맞춰 문구 구성
        _card_count = len(request.cards) if request.cards else 0
        if _card_count == 1:
            _answer_instr = "위 한 장의 카드로 질문에 답해줘"
            _format_instr = "카드 한 장이니까 문단 나눌 필요 없이 자연스럽게 풀어"
            _summary_instr = "마지막에 핵심 메시지 한 줄"
        elif _card_count == 2:
            _answer_instr = "위 두 장의 카드로 질문에 답해줘"
            _format_instr = "카드 두 장을 차례로 짚어줘. 카드마다 문단을 나눠서 써"
            _summary_instr = "마지막에 두 장을 종합한 조언 문단 하나"
        elif _card_count >= 3:
            _answer_instr = f"위 {_card_count}장의 카드로 질문에 답해줘"
            _format_instr = "카드를 한 장씩 차례로 짚어줘. 카드마다 문단을 나눠서(사이에 빈 줄) 써"
            _summary_instr = f"맨 마지막에 {_card_count}장을 종합한 조언 문단 하나"
        else:
            _answer_instr = "카드로 질문에 답해줘"
            _format_instr = "자연스러운 문장 흐름으로"
            _summary_instr = "핵심 메시지 한 줄"

        # 0단계: 카드 해석과 진단
        # 1단계: 카드 의미는 다시 풀지 않고 행동 가이드만
        if _followup_depth == 0:
            # 0단계: 카드 해석
            card_instruction = f"""타로 운세 풀이 요청 (0단계 = 카드 해석·진단)

질문: {sanitized_question}

[뽑힌 카드. 아래 정보를 근거로 해석할 것]
{card_context_block}
{spread_context}

{_answer_instr}.

[말투]
- 친한 친구가 옆에서 말해주듯 자연스럽게. 반말로.
- 제목, 헤더(###), 번호 목록(1. 2. 3.), <strong> 같은 태그·마크다운 기호는 절대 쓰지 마.

[형식 — 카드별로 문단 나누기]
- {_format_instr}.
- 각 문단은 그 카드 이름을 자연스럽게 언급하며 시작.
- {_summary_instr}.
- 각 문단은 3~4문장 이내로 짧게.

[톤 — 현실적이되 희망]
- 어려운 카드가 나와도 "이렇게 하면 풀려" 하고 빠져나갈 길을 보여줘.
- 역방향 카드의 부정 의미를 탓하듯 X → "요즘 좀 지쳐 있나 봐" 처럼 따뜻하게.

[내용]
- 막연한 말("긍정적으로 생각해") 금지.
- 각 카드의 의미를 질문 상황에 직접 연결.

🚨 절대 규칙: 사용자가 뽑은 카드는 **{_card_count}장**. 다른 개수 단언 X.
{rag_knowledge_text}"""
        else:
            # 1단계: 행동 가이드만
            card_instruction = f"""[1단계 — 행동 가이드 전용]

사용자가 뽑은 카드: {', '.join(card_details)}
질문: {sanitized_question}

🚨🚨🚨 절대 금지:
- ❌ 카드 의미 풀이 다시 ("달은 환상의 카드"...)
- ❌ 카드 이미지 설명
- ❌ 카드 위치별 진단 재서술
→ 위 모두 0단계에서 이미 받았음. 1단계는 *그 카드들이 가리키는 행동 가이드*만.

✅ 1단계가 다룰 것:
1. 0단계가 못 짚은 *숨은 패턴* (카드 간 상호작용, 핵심 갈등)
2. 구체 행동 (시간·장소·방법 디테일)
3. 시간 축 (카드 전통 — 완드=일, 검=주, 컵=월, 펜타클=분기)
4. 안 해야 할 것
5. 행동의 기대 효과

[응답 구조 — 4단락 / 반드시]
단락 1: 시그니처 ("그래서 어떻게 풀어가볼까 -") + 공감 한 줄 + 처음에 못 짚은 숨은 패턴
단락 2: 이번 주 가장 작은 한 발 (구체 행동 두세 개)
단락 3: 다음 주~2주 흐름 잡기
단락 4: 마무리 (매번 다른 표현, 클리셰 X)

[길이]
🚨 반드시 900~1100자, 4단락, 15~20줄. 진단의 두 배 깊이.
800자 미만이면 응답 부족 — 더 풍부하게.

🚨🚨🚨 응답에 절대 박지 마 (시스템 용어·존댓말):
❌ "0단계", "1단계", "follow-up", "이어보기" 같은 시스템 용어 사용자에게 노출 X
❌ "해드렸", "드렸", "드릴" 존댓말 X → 반말만 ("해줬", "줬어", "줄게")
❌ "~세요", "~해보세요" X → "~봐", "~해봐"

🚨 절대 규칙: 사용자가 뽑은 카드는 **{_card_count}장**. 다른 개수 단언 X.
"""

        messages.append({"role": "system", "content": card_instruction})
    else:
        # 일반 대화 (기록은 있고 카드는 없음): 현재 질문을 user 메시지로 추가.
        # 이게 없으면 모델이 빈 응답(0 chars)을 돌려줌.
        messages.append({"role": "user", "content": sanitized_question})

    async def generate_streaming_response():
        global _llm_waiting
        acquire_task = None
        slot_held = False
        try:
            # 동시 처리 게이트
            # 슬롯이 비면 즉시 통과. 차 있으면 3초마다 대기 순번을 흘려보내며 기다림.
            _llm_waiting += 1
            acquire_task = asyncio.ensure_future(_llm_semaphore.acquire())
            while True:
                done, _ = await asyncio.wait({acquire_task}, timeout=3.0)
                if done:
                    slot_held = True
                    break
                yield f"data: {json.dumps({'type': 'queue', 'waiting': _llm_waiting, 'session_id': session_id})}\n\n"
            _llm_waiting -= 1

            # 모델 및 옵션 선택 (인사말/Follow-up/카드 해석/일반 대화 구분)
            _fd = int(request.context_info.get('followup_depth', 0) or 0)

            if not request.conversation_history and not request.question:
                # 인사말
                model_type = "heavy"
                temperature = 0.5
                max_tokens = 256
            elif _fd > 0:
                # Follow-up(이어보기)
                # mlx 모델 응답이 더 길게 나와서(평균 1171자 vs 969자) max_tokens를 넉넉히 잡음
                model_type = "heavy"
                # Qwen3 non-thinking 모드 권장값
                temperature = 0.7   # 0.85 이상은 끝없이 생성하는 경우가 있음
                max_tokens = 6000   # 4000에서도 잘려서 6000
                print(f"⏱️ Follow-up depth={_fd} → temp={temperature}, max_tokens={max_tokens}")
            elif request.cards:
                # 첫 카드 해석 (0단계)
                # 900일 때 0단계 응답의 80%가 문장 중간에서 잘려서 1800으로 올렸는데,
                # 1800 고정은 3장 기준이라 5장 스프레드가 3장째에서 잘렸다. 카드 수에 비례해 잡는다.
                # 길이는 프롬프트로 제어하고 max_tokens는 안전 상한 역할만
                model_type = "heavy"
                temperature = 0.8
                _n_cards = max(1, len(request.cards or []))
                if request.reading_type == "premium":
                    max_tokens = 4096 + 400 * max(0, _n_cards - 3)
                else:
                    # 도입·종합·마무리 약 900t + 카드당 약 320t
                    max_tokens = min(6000, 900 + 320 * _n_cards)
                print(f"⏱️ 카드 {_n_cards}장, max_tokens={max_tokens}")
            else:
                # 일반 대화
                model_type = "heavy"
                temperature = 0.7
                max_tokens = 1400

            try:
                print(f"⏱️ [{time.time() - start_time:.2f}s] AI 스트리밍 시작 (모델: {model_type}, provider: {AI_PROVIDER})")
                full_response = ""
                first_token_logged = False
                is_first_chunk = True

                _force_claude_for_followup = False
                _use_model_type = model_type

                # 위기 신호 감지: Tier 1 키워드 + Tier 2 LLM 분류, 3인칭은 제외
                # Tier 1: 명백한 직접 표현. LLM 없이 바로 처리
                _crisis_explicit = [
                    '자살', '자해', '리스트컷',
                    '죽고 싶', '죽고싶', '뒤지고 싶', '뒤지고싶',
                    '살기 싫어', '살기싫어',
                    '살고 싶지 않', '살고싶지 않', '살고 싶지않', '살고싶지않',
                ]
                # Tier 2: 애매한 우회 표현. LLM으로 분류
                _crisis_ambiguous = [
                    '사라지', '없어지', '안 깨어', '안깨어', '안 떴으면', '안떴으면',
                    '눈 안 떴', '잠들면 안', '아침이 안 왔', '내일이 안',
                    '끝내고 싶', '끝내고싶', '끝내버리', '그만 살', '그만살',
                    '편하게 가고', '편할 것 같', '편할것같', '다 편할',
                    '나만 없', '나 없으면', '내가 없으면',
                    '안 찾을', '못 찾을', '모두에게 작별', '마지막 인사',
                    '살 가치', '살 이유 없', '살아갈 이유',
                    '도망가고 싶', '아무도 모르게',
                    '모든 게 끝', '다 끝났', '인생 끝',
                    '희망 없어', '희망없어', '희망이 없',
                    '의미 없어', '의미없어', '존재 이유',
                    '몸에 상처', '상처내', '상처 내',
                    '벌 받고', '벌받고',
                    '내가 미워서', '내가 너무 미워',
                    '견딜 수가 없', '견딜수가없',
                    '약 한 번에', '약 다 먹', '약 한꺼번에', '약 먹어',
                    '죽음이 두렵지 않', '죽는 게 더 편',
                    '이 세상에 없', '세상에서 없어',
                    '나 좀 데려가',
                ]
                # 3인칭 제외 (본인이 아닌 타인 걱정)
                _third_person = ['친구가', '엄마가', '아빠가', '동생이', '오빠가', '언니가',
                                  '그 사람이', '그사람이', '그애가', '걔가', '그녀가', '그가',
                                  '선배가', '후배가', '동료가', '남친이', '여친이', '남편이', '아내가',
                                  '아들이', '딸이', '부모님이']

                _crisis_check_text = (sanitized_question or '').lower()
                _has_third_person = any(tp in _crisis_check_text for tp in _third_person)
                _is_crisis = False

                if not _has_third_person:
                    # Tier 1이면 바로 위기
                    if any(kw in _crisis_check_text for kw in _crisis_explicit):
                        _is_crisis = True
                        print(f"🚨 위기 Tier1 (명백 키워드): {sanitized_question[:50]}")
                    # Tier 2는 LLM 분류
                    elif any(kw in _crisis_check_text for kw in _crisis_ambiguous):
                        _is_crisis = await classify_crisis_with_llm(sanitized_question)
                        print(f"🚨 위기 Tier2 LLM 판정 = {_is_crisis}: {sanitized_question[:50]}")
                elif any(kw in _crisis_check_text for kw in _crisis_explicit + _crisis_ambiguous):
                    print(f"ℹ️ 3인칭 위기 표현 — 본인 위기 X로 처리: {sanitized_question[:50]}")
                if _is_crisis:
                    print(f"🚨 위기 신호 감지: 자살·자해 키워드 발견. 응답 앞·뒤 안내 강제 박기")
                    _crisis_prepend = (
                        "💛 잠깐, 그 마음 너무 무겁다면 들어볼게.\n"
                        "혼자 끙끙대지 마. 전문가가 진짜 잘 들어줄 거야.\n"
                        "📞 1393 (자살예방) · 1577-0199 (정신건강위기) — 24시간 무료\n"
                        "\n"
                        "─────────────────────\n"
                        "\n"
                    )
                    full_response += _crisis_prepend
                    yield f"data: {json.dumps({'content': _crisis_prepend, 'session_id': session_id})}\n\n"

                async for chunk_data in call_ai_streaming(
                    messages=messages,
                    system_prompt="",  # 이미 messages에 시스템 프롬프트 포함됨
                    model_type=_use_model_type,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    force_claude=_force_claude_for_followup,
                ):
                    if _force_claude_for_followup or AI_PROVIDER == "CLAUDE":
                        # Claude: 문자열 chunk
                        content = chunk_data
                        done_flag = False
                    else:
                        # Ollama: {"content", "done"} dict
                        # fake-streaming 마지막 chunk는 done=True이면서 content도 있어서 content부터 처리
                        content = chunk_data.get("content", "")
                        done_flag = chunk_data.get("done", False)

                    # 첫 청크에서 앞부분의 <br> 태그 제거
                    if is_first_chunk and content:
                        content = re.sub(r'^(\s*<br\s*/?\s*>|\s*\n)+', '', content, flags=re.IGNORECASE)
                        is_first_chunk = False

                    # 중국어 문장 제거 (2글자 이상 연속 한자)
                    content = clean_chinese(content)

                    if content:
                        full_response += content
                        yield f"data: {json.dumps({'content': content, 'session_id': session_id})}\n\n"

                    # 첫 토큰 수신 시간 로그
                    if not first_token_logged and content:
                        print(f"⏱️ [{time.time() - start_time:.2f}s] ✅ 첫 토큰 수신 완료")
                        first_token_logged = True

                    # content 처리 후 done이면 종료 (Ollama만 해당)
                    if done_flag:
                        break

                # 위기 신호면 응답 끝에 안내를 한 번 더 붙임
                if _is_crisis:
                    _crisis_append = (
                        "\n\n─────────────────────\n"
                        "💛 다시 한 번 — 마음이 너무 힘들면 혼자 견디지 마.\n"
                        "📞 1393 자살예방상담 · 1577-0199 정신건강위기 — 거기 사람들 진짜 잘 들어줘."
                    )
                    full_response += _crisis_append
                    yield f"data: {json.dumps({'content': _crisis_append, 'session_id': session_id})}\n\n"

                print(f"⏱️ [{time.time() - start_time:.2f}s] AI 스트리밍 완료 ({len(full_response)} chars)")

                # 스트리밍 완료 후 처리
                # 카드를 뽑았을 때만 타로 해석 기록에 저장
                reading_id = None
                if full_response and request.cards:
                    current_user_id = None
                    if AUTH_AVAILABLE:
                        try:
                            current_user_id = await get_current_user_id(http_request)
                        except Exception as e:
                            print(f"⚠️ 유저 ID 조회 실패: {e}")
                    reading_id = await save_reading_to_db(session_id, sanitized_question, request.cards, full_response, db, user_id=current_user_id)
                    print(f"⏱️ [{time.time() - start_time:.2f}s] DB 저장 완료 (reading_id={reading_id})")

                    # 포인트 사용인 경우 포인트 차감, 아니면 일일 사용량 증가
                    if request.use_points and AUTH_AVAILABLE and POINTS_AVAILABLE:
                        try:
                            user_id = await get_current_user_id(http_request)
                            if user_id:
                                feature = "premium_reading" if request.reading_type == "premium" else "extra_reading"
                                cost = await get_feature_cost(feature, db)
                                new_balance = await consume_points(user_id, cost, feature, db)
                                print(f"⏱️ [{time.time() - start_time:.2f}s] 포인트 차감: {cost}pt (잔액: {new_balance}pt)")
                        except Exception as e:
                            print(f"⚠️ 포인트 차감 실패: {e}")
                    else:
                        await increment_daily_usage(session_id, db)

                yield f"data: {json.dumps({'done': True, 'session_id': session_id, 'reading_id': reading_id})}\n\n"

                print(f"{'='*60}")
                print(f"⏱️ 총 소요 시간: {time.time() - start_time:.2f}s")
                print(f"{'='*60}\n")

                return

            except Exception as e:
                print(f"❌ Streaming error: {e}")
                yield f"data: {json.dumps({'error': '서비스가 일시적으로 이용할 수 없어.', 'session_id': session_id})}\n\n"
                return

        except Exception as e:
            print(f"❌ Generation error: {e}")
            yield f"data: {json.dumps({'error': '서비스가 일시적으로 이용할 수 없어.', 'session_id': session_id})}\n\n"
            return
        finally:
            # 동시 처리 게이트 정리
            if slot_held:
                _llm_semaphore.release()
            else:
                # 슬롯을 잡기 전에 중단된 경우 (클라이언트 연결 끊김 등)
                _llm_waiting -= 1
                if acquire_task is not None and not acquire_task.done():
                    acquire_task.cancel()
                elif acquire_task is not None and not acquire_task.cancelled():
                    # 취소 직전 슬롯을 넘겨받았다면 반환
                    _llm_semaphore.release()
            await db.close()

    return StreamingResponse(
        generate_streaming_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "https://serapina.kr",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )

@app.get("/readings/{session_id}")
async def get_session_readings(session_id: str, db: AsyncSession = Depends(get_database)):
    """Get last 5 readings for a session with decryption"""
    from sqlalchemy import select

    # 데이터베이스 연결 실패 시 빈 리스트 반환
    if db is None:
        return []

    result = await db.execute(
        select(TarotReading).where(TarotReading.session_id == session_id).order_by(TarotReading.timestamp.desc()).limit(5)
    )
    readings = result.scalars().all()
    
    encryption = get_encryption()
    decrypted_readings = []
    
    for reading in readings:
        try:
            decrypted_question = encryption.decrypt_text(reading.question) if reading.question else ""
            decrypted_response = encryption.decrypt_text(reading.ai_response) if reading.ai_response else ""
            
            # 카드 데이터 복호화
            if reading.selected_cards:
                try:
                    decrypted_cards = encryption.decrypt_json(reading.selected_cards)
                    if isinstance(decrypted_cards, str):
                        decrypted_cards = json.loads(decrypted_cards)
                except Exception as e:
                    # 복호화 실패 시 기존 방식으로 처리
                    print(f"⚠️ 카드 복호화 실패 (id={reading.id}): {e}")
                    decrypted_cards = json.loads(reading.selected_cards)
            else:
                decrypted_cards = []
            
            decrypted_readings.append({
                "id": reading.id,
                "question": decrypted_question,
                "cards": decrypted_cards,
                "response": decrypted_response,
                "timestamp": reading.timestamp.isoformat(),
                "is_saved": reading.is_saved
            })
        except Exception as e:
            # 복호화 실패 시 원본 데이터 사용 (기존 암호화되지 않은 데이터일 수 있음)
            print(f"⚠️ 리딩 복호화 실패 (id={reading.id}): {e}")
            decrypted_readings.append({
                "id": reading.id,
                "question": reading.question,
                "cards": json.loads(reading.selected_cards) if reading.selected_cards else [],
                "response": reading.ai_response,
                "timestamp": reading.timestamp.isoformat(),
                "is_saved": reading.is_saved
            })
    
    return {
        "session_id": session_id,
        "readings": decrypted_readings
    }

@app.post("/save-reading")
async def save_reading(request: SaveReadingRequest, http_request: Request = None, db: AsyncSession = Depends(get_database)):
    """Mark a reading as saved"""
    from sqlalchemy import update, select

    # 세션 기반 또는 유저 기반 인증
    query = select(TarotReading).where(TarotReading.id == request.reading_id)

    # 유저 인증 시 user_id로도 매칭
    user_id = None
    if AUTH_AVAILABLE and http_request:
        try:
            user_id = await get_current_user_id(http_request)
        except Exception as e:
            print(f"⚠️ 리딩 저장 시 유저 인증 실패: {e}")

    if user_id:
        query = query.where(TarotReading.user_id == user_id)
    else:
        query = query.where(TarotReading.session_id == request.session_id)

    result = await db.execute(query)
    reading = result.scalar_one_or_none()
    if not reading:
        raise HTTPException(status_code=404, detail="리딩을 찾을 수 없어요")

    reading.is_saved = True
    await db.commit()

    return {"message": "Reading saved successfully", "is_saved": True}

class FeedbackRequest(BaseModel):
    session_id: str
    rating: int
    categories: list[str]
    comment: str
    contact: str

class ContactRequest(BaseModel):
    session_id: str
    type: str
    name: str
    email: str
    message: str

@app.post("/submit-feedback")
async def submit_feedback(request: FeedbackRequest, db: AsyncSession = Depends(get_database)):
    """사용자 평점 피드백 저장"""
    if db is None:
        return {"message": "Feedback saved locally"}

    try:
        from database import UserRating

        # user_ratings 테이블에 저장
        rating = UserRating(
            session_id=request.session_id,
            rating=request.rating,
            categories=request.categories,
            comment=request.comment if request.comment else None,
            contact=request.contact if request.contact else None
        )
        db.add(rating)
        await db.commit()

        print(f"✅ 평점 피드백 저장 성공: {request.session_id} - {request.rating}/5")
        return {"message": "Feedback submitted successfully", "success": True}
    except Exception as e:
        print(f"❌ 평점 피드백 저장 오류: {e}")
        import traceback
        print(traceback.format_exc())
        return {"message": "Feedback saved locally", "success": False}

@app.post("/submit-contact")
async def submit_contact(request: ContactRequest, db: AsyncSession = Depends(get_database)):
    """문의하기 저장"""
    if db is None:
        return {"message": "Contact saved locally"}

    try:
        from database import UserContact

        contact = UserContact(
            session_id=request.session_id,
            contact_type=request.type,
            name=request.name,
            email=request.email,
            message=request.message,
            status='pending'
        )
        db.add(contact)
        await db.commit()

        print(f"✅ 문의하기 저장 성공: {request.name} ({request.email}) - {request.type}")
        return {"message": "Contact submitted successfully", "success": True}
    except Exception as e:
        print(f"❌ 문의하기 저장 오류: {e}")
        import traceback
        print(traceback.format_exc())
        return {"message": "Contact saved locally", "success": False}

class SpreadSelectionResponse(BaseModel):
    spreadType: str
    cardCount: int
    cardPositions: list[str]

@app.post("/select_spread", response_model=SpreadSelectionResponse)
async def select_spread(request: PredictionScoreRequest):
    """질문에 맞는 스프레드 선택. LLM 실패 시 키워드 폴백"""


    question_lower = request.question.lower()

    # 스프레드 정의는 spreads.py 한 곳에서 관리한다. 일/주/월/연 스프레드의 카드 위치는
    # 지금 시점 기준으로 만들고, '이번 주' 질문에 '다음 주 월요일' 같은 자리가 섞이지 않게 한다.
    import pytz
    from datetime import datetime
    from spreads import SPREADS, get_spread, build_catalog_text

    now_kst = datetime.now(pytz.timezone('Asia/Seoul'))
    spread_options = {}
    for _name in SPREADS:
        _cnt, _pos, _win = get_spread(_name, request.question, now_kst)
        spread_options[_name] = {"cardCount": _cnt, "cardPositions": _pos, "window": _win}

    # 1차: 규칙 기반 의도 판정 (question_intent.py).
    # 이게 없을 때 "이번주에 가능할까?"가 '이번주' 때문에 주간운세로 가서
    # 되냐 안 되냐에는 답하지 않는 리딩이 나갔다.
    try:
        from question_intent import detect_intent
        _it = detect_intent(request.question)
        if _it["confident"] and _it["spread"] in spread_options:
            _sp = spread_options[_it["spread"]]
            print(f"✅ 의도 판정: {_it['intent']}, {_it['spread']} ({_it['reason']})")
            return SpreadSelectionResponse(
                spreadType=_it["spread"],
                cardCount=_sp["cardCount"],
                cardPositions=_sp["cardPositions"],
            )
        print(f"ℹ️ 의도 불명확({_it['intent']}), LLM 판단으로 넘김")
    except Exception as _e:
        print(f"⚠️ 의도 판정 실패, LLM으로 진행: {_e}")

    prompt = f"""당신은 10대 여학생들의 질문에 가장 적합한 타로카드 스프레드를 추천하는 전문가입니다.

사용 가능한 스프레드:
{build_catalog_text()}

사용자 질문: "{request.question}"

⚠️ 중요한 판단 기준:
- "오늘", "내일", "모레" → 일일운세 (3장)
- "이번 주", "다음 주" → 주간운세 (3장)
- "이번 달", "다음 달" → 월간운세 (5장)
- "올해", "내년" → 연간운세 (5장)
- "남친/여친과", "우리 사이" → 사귀는중운세 (4장)
- "썸", "밀당" → 썸운세 (4장)
- "짝사랑", "좋아하는 애" → 짝사랑운세 (4장)
- "연인 만날까", "언제 생길까" → 소개팅/만남운세 (3장)
- "A할까 B할까", "둘 중 뭐", "갈까 말까" → 선택 (5장)
- "언제 연락 올까", "얼마나 걸려" → 시기 (3장)
- "그 사람 속마음", "무슨 생각일까" → 속마음 (4장)
- "왜 이럴까", "뭐가 문제야" → 원인-해결 (4장)
- "엄마랑", "친구랑", "팀장이랑" 등 사람 사이 갈등 → 관계 (5장)
- 오래 묵은 복잡한 고민, "전부 다 봐줘" → 켈틱크로스 (10장)

⚠️ 시간 표현이 질문에 있으면 시간 스프레드를 최우선으로 고른다.
⚠️ 켈틱크로스는 10장이라 부담이 크다. 질문이 짧거나 단순하면 고르지 마.

위 질문에 가장 적합한 스프레드 하나를 선택하여 JSON 형식으로만 응답해.
스프레드 이름만 정확히 골라줘 (장수·위치는 시스템이 자동으로 채움).

{{"spreadType": "선택한 스프레드 이름"}}
"""

    try:
        ai_response_content = await call_ai_non_streaming(
            prompt=prompt,
            model_type="light",
            temperature=0.3,
            max_tokens=256
        )

        import json
        parsed_response = json.loads(ai_response_content)

        print(f"✅ AI가 선택한 스프레드: {parsed_response['spreadType']}")

        # LLM은 spreadType만 신뢰하고 cardCount/cardPositions는 코드 테이블에서 가져옴
        # (LLM이 장수와 위치 개수를 어긋나게 생성하는 버그 방지)
        # LLM이 '속마음운세', '시기 (3장)'처럼 이름을 흘려 쓰는 일이 잦아 정규화한다.
        # 정규화 없이 조회하면 조용히 기본 스프레드로 떨어진다.
        from spreads import resolve_spread_name
        ai_spread_type = resolve_spread_name(parsed_response.get('spreadType'))
        if ai_spread_type and ai_spread_type in spread_options:
            spread = spread_options[ai_spread_type]
            print(f"   정규화된 스프레드: {ai_spread_type} ({spread['cardCount']}장)")
            return SpreadSelectionResponse(
                spreadType=ai_spread_type,
                cardCount=spread['cardCount'],
                cardPositions=spread['cardPositions']
            )
        # 테이블에 없는 이름이면 기본 스프레드로 폴백
        spread = spread_options["과거-현재-미래"]
        return SpreadSelectionResponse(
            spreadType="과거-현재-미래",
            cardCount=spread['cardCount'],
            cardPositions=spread['cardPositions']
        )

    except Exception as e:
        print(f"⚠️ 스프레드 선택 오류: {str(e)}")
        
        # 질문 키워드 기반 폴백 로직
        question_lower = request.question.lower()
        
        # 연애 세분화 (체크 순서 중요)
        # 1. 새로운 만남/소개팅 (가장 먼저)
        if any(word in question_lower for word in ['만날', '만나', '생길', '소개팅', '인연', '새로운', '언제', '시기']):
            spread = spread_options["소개팅/만남운세"]
            print(f"✅ 선택된 스프레드: 소개팅/만남운세")
            return SpreadSelectionResponse(spreadType="소개팅/만남운세", cardCount=spread['cardCount'], cardPositions=spread['cardPositions'])
        # 2. 이별/재회
        elif any(word in question_lower for word in ['헤어', '이별', '재회', '다시', '전남친', '전여친', '복연']):
            spread = spread_options["이별/재회운세"]
            print(f"✅ 선택된 스프레드: 이별/재회운세")
            return SpreadSelectionResponse(spreadType="이별/재회운세", cardCount=spread['cardCount'], cardPositions=spread['cardPositions'])
        # 3. 사귀는 중
        elif any(word in question_lower for word in ['남친', '여친', '사귀', '우리', '애인', '커플']):
            spread = spread_options["사귀는중운세"]
            print(f"✅ 선택된 스프레드: 사귀는중운세")
            return SpreadSelectionResponse(spreadType="사귀는중운세", cardCount=spread['cardCount'], cardPositions=spread['cardPositions'])
        # 4. 썸
        elif any(word in question_lower for word in ['썸', '애매', '밀당', '연락', '카톡', '문자']):
            spread = spread_options["썸운세"]
            print(f"✅ 선택된 스프레드: 썸운세")
            return SpreadSelectionResponse(spreadType="썸운세", cardCount=spread['cardCount'], cardPositions=spread['cardPositions'])
        # 5. 짝사랑
        elif any(word in question_lower for word in ['짝사랑', '좋아하는', '관심', '마음', '고백']):
            spread = spread_options["짝사랑운세"]
            print(f"✅ 선택된 스프레드: 짝사랑운세")
            return SpreadSelectionResponse(spreadType="짝사랑운세", cardCount=spread['cardCount'], cardPositions=spread['cardPositions'])
        # 6. 일반 연애
        elif any(word in question_lower for word in ['연애', '사랑', '좋아', '결혼', '남자친구', '여자친구']):
            spread = spread_options["연애운세"]
            print(f"✅ 선택된 스프레드: 연애운세")
            return SpreadSelectionResponse(spreadType="연애운세", cardCount=spread['cardCount'], cardPositions=spread['cardPositions'])
        elif any(word in question_lower for word in ['진로', '직업', '취업', '일', '회사']):
            spread = spread_options["진로운세"]
            return SpreadSelectionResponse(spreadType="진로운세", cardCount=spread['cardCount'], cardPositions=spread['cardPositions'])
        elif any(word in question_lower for word in ['돈', '재물', '투자', '경제']):
            spread = spread_options["재물운세"]
            return SpreadSelectionResponse(spreadType="재물운세", cardCount=spread['cardCount'], cardPositions=spread['cardPositions'])
        elif any(word in question_lower for word in ['시험', '공부', '성적', '학교', '학업']):
            spread = spread_options["학업운세"]
            return SpreadSelectionResponse(spreadType="학업운세", cardCount=spread['cardCount'], cardPositions=spread['cardPositions'])
        elif any(word in question_lower for word in ['친구', '우정', '단짝', '반', '친구들']):
            spread = spread_options["우정운세"]
            return SpreadSelectionResponse(spreadType="우정운세", cardCount=spread['cardCount'], cardPositions=spread['cardPositions'])
        elif any(word in question_lower for word in ['건강', '몸']):
            spread = spread_options["건강운세"]
            return SpreadSelectionResponse(spreadType="건강운세", cardCount=spread['cardCount'], cardPositions=spread['cardPositions'])
        elif any(word in question_lower for word in ['예스', '노', '맞나', '할까', '해야']):
            spread = spread_options["예스/노"]
            return SpreadSelectionResponse(spreadType="예스/노", cardCount=spread['cardCount'], cardPositions=spread['cardPositions'])
        else:
            # 기본값으로 과거-현재-미래 스프레드 사용
            spread = spread_options["과거-현재-미래"]
            return SpreadSelectionResponse(spreadType="과거-현재-미래", cardCount=spread['cardCount'], cardPositions=spread['cardPositions'])

# 광고 노출/클릭 추적
class AdTrackingRequest(BaseModel):
    session_id: str
    ad_type: str  # 'display', 'interstitial', 'rewarded'
    ad_placement: str  # 'chat', 'card_selection', 'daily_limit'

@app.post("/api/track-ad-impression")
async def track_ad_impression(request: AdTrackingRequest, db: AsyncSession = Depends(get_database)):
    """광고 노출 추적"""
    if db is None:
        return {"status": "ok", "message": "Database not available"}

    try:
        from sqlalchemy import select
        impression = AdImpression(
            session_id=request.session_id,
            ad_type=request.ad_type,
            ad_placement=request.ad_placement,
            impression_date=get_kst_today()
        )
        db.add(impression)
        await db.commit()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/track-ad-click")
async def track_ad_click(request: AdTrackingRequest, db: AsyncSession = Depends(get_database)):
    """광고 클릭 추적"""
    if db is None:
        return {"status": "ok", "message": "Database not available"}

    try:
        from sqlalchemy import select
        click = AdClick(
            session_id=request.session_id,
            ad_type=request.ad_type,
            ad_placement=request.ad_placement,
            click_date=get_kst_today()
        )
        db.add(click)
        await db.commit()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Blog API

@app.get("/blog")
async def get_blog_posts(
    category: str = None,
    limit: int = 100,
    offset: int = 0,
    sort: str = "recent",
    db: AsyncSession = Depends(get_database)
):
    """블로그 포스트 목록 조회"""
    if not DATABASE_AVAILABLE or db is None:
        return {"posts": [], "total": 0}

    try:
        from sqlalchemy import select, func

        query = select(BlogPost).where(BlogPost.published == True)

        # Category filter
        if category:
            query = query.where(BlogPost.category == category)

        # Order by sort type
        if sort == "popular":
            query = query.order_by(BlogPost.view_count.desc())
        else:
            # Default: Order by published date (newest first)
            query = query.order_by(BlogPost.published_at.desc())

        count_query = select(func.count()).select_from(BlogPost).where(BlogPost.published == True)
        if category:
            count_query = count_query.where(BlogPost.category == category)

        result = await db.execute(count_query)
        total = result.scalar()

        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        posts = result.scalars().all()

        posts_data = []
        for post in posts:
            posts_data.append({
                "id": post.id,
                "title": post.title,
                "category": post.category,
                "excerpt": post.excerpt,
                "tags": post.tags,
                "gradient": post.gradient,
                "emoji": post.emoji,
                "published_at": post.published_at.strftime("%Y-%m-%d"),
                "view_count": post.view_count
            })

        return {"posts": posts_data, "total": total}

    except Exception as e:
        print(f"Error fetching blog posts: {e}")
        return {"posts": [], "total": 0}

@app.get("/blog/{post_id}")
async def get_blog_post(
    post_id: int,
    db: AsyncSession = Depends(get_database)
):
    """블로그 포스트 상세 조회"""
    if not DATABASE_AVAILABLE or db is None:
        return {"error": "Database not available"}

    try:
        from sqlalchemy import select, update

        query = select(BlogPost).where(BlogPost.id == post_id, BlogPost.published == True)
        result = await db.execute(query)
        post = result.scalar_one_or_none()

        if not post:
            return {"error": "Post not found"}

        update_query = update(BlogPost).where(BlogPost.id == post_id).values(view_count=BlogPost.view_count + 1)
        await db.execute(update_query)
        await db.commit()

        # Format content as HTML (not used for display but kept for compatibility)
        content_html = f"""
        <div class="blog-content">
            <section class="situation-section">
                <p>{post.situation}</p>
            </section>

            <section class="cards-section">
                <div class="cards-list">
                    {"".join([f'<div class="card-item"><strong>{card}</strong></div>' for card in post.cards])}
                </div>
            </section>

            <section class="interpretation-section">
                {"".join([f'<div class="interpretation-item"><h3>{interp["card"]}</h3><p>{interp["meaning"]}</p></div>' for interp in post.interpretations])}
            </section>

            <section class="advice-section">
                <blockquote>{post.advice}</blockquote>
            </section>
        </div>
        """

        return {
            "id": post.id,
            "title": post.title,
            "content": content_html,
            "category": post.category,
            "excerpt": post.excerpt,
            "situation": post.situation,
            "cards": post.cards,
            "interpretations": post.interpretations,
            "advice": post.advice,
            "tags": post.tags,
            "recommended_mbti": post.recommended_mbti or [],
            "gradient": post.gradient,
            "emoji": post.emoji,
            "published_at": post.published_at.strftime("%Y-%m-%d"),
            "view_count": post.view_count + 1
        }

    except Exception as e:
        print(f"Error fetching blog post: {e}")
        return {"error": str(e)}

@app.get("/sitemap.xml")
@app.head("/sitemap.xml")
async def generate_sitemap(db: AsyncSession = Depends(get_database)):
    """동적 sitemap.xml 생성 (GET, HEAD 모두 지원)"""
    from datetime import datetime

    base_url = "https://serapina.kr"
    today = datetime.now().strftime("%Y-%m-%d")

    # 정적 페이지 URL
    static_urls = [
        {"loc": f"{base_url}/", "lastmod": today, "changefreq": "daily", "priority": "1.0"},
        {"loc": f"{base_url}/cards", "lastmod": today, "changefreq": "weekly", "priority": "0.9"},
        {"loc": f"{base_url}/cards/major-arcana", "lastmod": today, "changefreq": "weekly", "priority": "0.8"},
        {"loc": f"{base_url}/cards/minor-arcana", "lastmod": today, "changefreq": "weekly", "priority": "0.8"},
        {"loc": f"{base_url}/guides", "lastmod": today, "changefreq": "weekly", "priority": "0.9"},
        {"loc": f"{base_url}/guides/love", "lastmod": today, "changefreq": "weekly", "priority": "0.8"},
        {"loc": f"{base_url}/guides/career", "lastmod": today, "changefreq": "weekly", "priority": "0.8"},
        {"loc": f"{base_url}/guides/study", "lastmod": today, "changefreq": "weekly", "priority": "0.8"},
        {"loc": f"{base_url}/guides/money", "lastmod": today, "changefreq": "weekly", "priority": "0.8"},
        {"loc": f"{base_url}/blog", "lastmod": today, "changefreq": "weekly", "priority": "0.9"},
        {"loc": f"{base_url}/today", "lastmod": today, "changefreq": "daily", "priority": "0.95"},
        {"loc": f"{base_url}/about", "lastmod": today, "changefreq": "monthly", "priority": "0.8"},
        {"loc": f"{base_url}/contact", "lastmod": today, "changefreq": "monthly", "priority": "0.7"},
        {"loc": f"{base_url}/privacy", "lastmod": today, "changefreq": "monthly", "priority": "0.7"},
        {"loc": f"{base_url}/terms", "lastmod": today, "changefreq": "monthly", "priority": "0.7"},
    ]

    # 슈트별 페이지
    for suit in ["wands", "cups", "swords", "pentacles"]:
        static_urls.append({
            "loc": f"{base_url}/cards/suit/{suit}",
            "lastmod": today,
            "changefreq": "monthly",
            "priority": "0.7"
        })

    # 메이저 아르카나 카드
    for i in range(22):
        static_urls.append({
            "loc": f"{base_url}/cards/maj{i:02d}",
            "changefreq": "monthly",
            "priority": "0.6"
        })

    # 마이너 아르카나 카드
    for suit in ["cups", "pents", "swords", "wands"]:
        for i in range(1, 15):
            static_urls.append({
                "loc": f"{base_url}/cards/{suit}{i:02d}",
                "changefreq": "monthly",
                "priority": "0.5"
            })

    # /today/:mbti (MBTI 16개별 오늘의 카드)
    for mbti in ["ENFP", "ENFJ", "ENTP", "ENTJ", "ESFP", "ESFJ", "ESTP", "ESTJ",
                 "INFP", "INFJ", "INTP", "INTJ", "ISFP", "ISFJ", "ISTP", "ISTJ"]:
        static_urls.append({
            "loc": f"{base_url}/today/{mbti}",
            "lastmod": today,
            "changefreq": "daily",
            "priority": "0.8"
        })

    # 블로그 포스트 (동적으로 가져오기)
    blog_urls = []
    if DATABASE_AVAILABLE and db is not None:
        try:
            from sqlalchemy import select
            query = select(BlogPost).where(BlogPost.published == True).order_by(BlogPost.published_at.desc())
            result = await db.execute(query)
            posts = result.scalars().all()

            for post in posts:
                # updated_at이 None이면 published_at 사용, 둘 다 없으면 오늘 날짜
                lastmod_date = post.updated_at or post.published_at
                lastmod = lastmod_date.strftime("%Y-%m-%d") if lastmod_date else today
                blog_urls.append({
                    "loc": f"{base_url}/blog/{post.id}",
                    "lastmod": lastmod,
                    "changefreq": "monthly",
                    "priority": "0.8"
                })
        except Exception as e:
            print(f"Error fetching blog posts for sitemap: {e}")

    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for url in static_urls:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>{url["loc"]}</loc>\n'
        if "lastmod" in url:
            xml_content += f'    <lastmod>{url["lastmod"]}</lastmod>\n'
        xml_content += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
        xml_content += f'    <priority>{url["priority"]}</priority>\n'
        xml_content += '  </url>\n'

    for url in blog_urls:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>{url["loc"]}</loc>\n'
        xml_content += f'    <lastmod>{url["lastmod"]}</lastmod>\n'
        xml_content += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
        xml_content += f'    <priority>{url["priority"]}</priority>\n'
        xml_content += '  </url>\n'

    xml_content += '</urlset>'

    return Response(content=xml_content, media_type="application/xml")

# 어드민 API (nginx Basic Auth로 보호)
ADMIN_INSTAGRAM_OUTPUT = "/var/today-data"  # nginx와 같은 마운트 경로. backend 컨테이너엔 마운트가 없어서 fallback 경로도 시도
ADMIN_INSTAGRAM_OUTPUT_FALLBACK = "/app/scripts/instagram/output"


def _list_instagram_files() -> list:
    """인스타 발행 콘텐츠 파일 목록 (날짜 순)"""
    import os
    base = ADMIN_INSTAGRAM_OUTPUT if os.path.isdir(ADMIN_INSTAGRAM_OUTPUT) else ADMIN_INSTAGRAM_OUTPUT_FALLBACK
    if not os.path.isdir(base):
        return []
    files = [f for f in os.listdir(base) if f.endswith(".json") and len(f) == len("2026-06-18.json")]
    files.sort()
    return [{"date": f[:-5], "path": os.path.join(base, f)} for f in files]


@app.get("/admin/dashboard")
async def admin_dashboard(db: AsyncSession = Depends(get_database)):
    """어드민 대시보드 지표"""
    from datetime import datetime, timedelta, date
    import os
    from sqlalchemy import select, func

    today = date.today()
    week_ago = today - timedelta(days=7)

    result = {
        "today": today.isoformat(),
        "stats": {},
        "instagram": {},
        "system": {},
    }

    # 세션/리딩 통계
    if DATABASE_AVAILABLE and db is not None:
        try:
            sessions_today = await db.execute(
                select(func.count()).select_from(TarotSession).where(func.date(TarotSession.created_at) == today)
            )
            readings_today = await db.execute(
                select(func.count()).select_from(TarotReading).where(func.date(TarotReading.timestamp) == today)
            )
            sessions_week = await db.execute(
                select(func.count()).select_from(TarotSession).where(TarotSession.created_at >= week_ago)
            )
            readings_week = await db.execute(
                select(func.count()).select_from(TarotReading).where(TarotReading.timestamp >= week_ago)
            )
            blog_published = await db.execute(
                select(func.count()).select_from(BlogPost).where(BlogPost.published == True)
            )
            blog_total = await db.execute(select(func.count()).select_from(BlogPost))

            result["stats"] = {
                "sessions_today": sessions_today.scalar() or 0,
                "readings_today": readings_today.scalar() or 0,
                "sessions_week": sessions_week.scalar() or 0,
                "readings_week": readings_week.scalar() or 0,
                "blog_published": blog_published.scalar() or 0,
                "blog_total": blog_total.scalar() or 0,
            }

            # 일별 7일치
            daily = await db.execute(
                select(
                    func.date(TarotReading.timestamp).label("day"),
                    func.count().label("cnt")
                ).where(TarotReading.timestamp >= week_ago).group_by(func.date(TarotReading.timestamp))
            )
            result["stats"]["daily_readings"] = [
                {"day": str(r.day), "count": r.cnt} for r in daily.all()
            ]
        except Exception as e:
            result["stats"]["error"] = str(e)

    # 인스타 발행 재고
    files = _list_instagram_files()
    future_files = [f for f in files if f["date"] >= today.isoformat()]
    result["instagram"] = {
        "total_files": len(files),
        "future_days": len(future_files),
        "next_date": future_files[0]["date"] if future_files else None,
        "last_date": files[-1]["date"] if files else None,
    }

    # 시스템 상태
    # 인스타 토큰 만료일 (env에서 추정)
    token_issued = os.getenv("INSTAGRAM_TOKEN_ISSUED_AT", "")  # 토큰 발급 시 기록해둔 날짜
    token_expires = None
    if token_issued:
        try:
            issued = datetime.fromisoformat(token_issued).date()
            token_expires = (issued + timedelta(days=60)).isoformat()
        except Exception:
            pass

    result["system"] = {
        "token_expires": token_expires,
        "token_days_left": (datetime.fromisoformat(token_expires).date() - today).days if token_expires else None,
    }

    return result


@app.get("/admin/instagram")
async def admin_instagram(limit: int = 14):
    """인스타 콘텐츠 미리보기 (다음 N일)"""
    import json
    from datetime import date as _date

    files = _list_instagram_files()
    today = _date.today().isoformat()
    future = [f for f in files if f["date"] >= today][:limit]

    result = []
    for f in future:
        try:
            with open(f["path"], "r", encoding="utf-8") as fp:
                data = json.load(fp)
            result.append({"date": f["date"], "items": data})
        except Exception as e:
            result.append({"date": f["date"], "error": str(e)})

    return {"days": result, "total_future": len(future)}


@app.get("/admin/blog")
async def admin_blog_list(db: AsyncSession = Depends(get_database)):
    """블로그 전체 목록 (published 토글용)"""
    if not DATABASE_AVAILABLE or db is None:
        return {"posts": []}
    try:
        from sqlalchemy import select
        result = await db.execute(select(BlogPost).order_by(BlogPost.id.desc()))
        posts = result.scalars().all()
        return {"posts": [
            {
                "id": p.id,
                "title": p.title,
                "category": p.category,
                "published": bool(p.published),
                "view_count": p.view_count or 0,
                "published_at": p.published_at.isoformat() if p.published_at else None,
            } for p in posts
        ]}
    except Exception as e:
        return {"posts": [], "error": str(e)}


class BlogToggleRequest(BaseModel):
    published: bool


@app.post("/admin/blog/{post_id}/toggle")
async def admin_blog_toggle(post_id: int, req: BlogToggleRequest, db: AsyncSession = Depends(get_database)):
    """블로그 published 토글"""
    if not DATABASE_AVAILABLE or db is None:
        return {"error": "DB not available"}
    try:
        from sqlalchemy import select, update
        from datetime import datetime as _dt
        await db.execute(
            update(BlogPost).where(BlogPost.id == post_id).values(
                published=req.published,
                published_at=_dt.now() if req.published else None,
            )
        )
        await db.commit()
        return {"ok": True, "id": post_id, "published": req.published}
    except Exception as e:
        await db.rollback()
        return {"error": str(e)}


@app.get("/admin/sessions")
async def admin_sessions(limit: int = 50, db: AsyncSession = Depends(get_database)):
    """최근 리딩 목록 (위기 키워드 감지 표시, 전체 본문 포함)"""
    if not DATABASE_AVAILABLE or db is None:
        return {"readings": []}

    CRISIS_KEYWORDS = ["자살", "죽고", "죽어", "죽고싶", "사라지고싶", "끝내고싶", "살기싫", "자해", "살아갈"]

    try:
        from sqlalchemy import select
        result = await db.execute(
            select(TarotReading).order_by(TarotReading.timestamp.desc()).limit(limit)
        )
        readings = result.scalars().all()

        out = []
        try:
            from encryption import get_encryption
            enc = get_encryption()
        except Exception:
            enc = None

        def _try_decrypt(val: str) -> str:
            if not val or not enc:
                return val or ""
            try:
                return enc.decrypt_text(val)
            except Exception:
                return val

        def _try_decrypt_cards(val: str) -> str:
            if not val or not enc:
                return val or ""
            try:
                cards = enc.decrypt_json(val)
                if isinstance(cards, list):
                    names = []
                    for c in cards:
                        if isinstance(c, dict):
                            names.append(c.get("name") or c.get("id") or str(c))
                        else:
                            names.append(str(c))
                    return ", ".join(names)
                return str(cards)
            except Exception:
                return val

        for r in readings:
            q = _try_decrypt(r.question or "")
            a = _try_decrypt(r.ai_response or "")
            cards = _try_decrypt_cards(r.selected_cards or "")
            crisis = any(kw in q for kw in CRISIS_KEYWORDS)
            out.append({
                "id": r.id,
                "session_id": r.session_id,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                "question": q,
                "response": a,
                "cards": cards,
                "reading_type": r.reading_type,
                "crisis": crisis,
            })

        return {"readings": out}
    except Exception as e:
        return {"readings": [], "error": str(e)}


# Auth (카카오 로그인)
try:
    from auth import (
        exchange_kakao_code, get_kakao_user_info,
        create_access_token, create_refresh_token,
        get_current_user_id, require_user_id, KAKAO_REST_API_KEY, KAKAO_REDIRECT_URI
    )
    AUTH_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Auth 모듈 로드 실패: {e}")
    AUTH_AVAILABLE = False


class KakaoCallbackRequest(BaseModel):
    code: str


class LinkSessionRequest(BaseModel):
    session_id: str


class EmailRegisterRequest(BaseModel):
    email: str
    password: str
    nickname: str = ""


class EmailLoginRequest(BaseModel):
    email: str
    password: str


if AUTH_AVAILABLE:
    import bcrypt

    @app.post("/auth/register")
    async def email_register(req: EmailRegisterRequest, db: AsyncSession = Depends(get_database)):
        """이메일/패스워드 회원가입"""
        if db is None:
            raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")

        email = req.email.strip().lower()
        if not email or "@" not in email:
            raise HTTPException(status_code=400, detail="올바른 이메일을 입력해주세요")
        if len(req.password) < 6:
            raise HTTPException(status_code=400, detail="비밀번호는 6자 이상이어야 해요")

        from sqlalchemy import select

        # 이메일 중복 확인
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="이미 가입된 이메일이에요")

        password_hash = bcrypt.hashpw(req.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        user = User(
            email=email,
            password_hash=password_hash,
            nickname=req.nickname or email.split("@")[0],
            point_balance=0,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "nickname": user.nickname,
                "profile_image": user.profile_image or "",
                "email": user.email,
                "point_balance": user.point_balance,
                "subscription_tier": user.subscription_tier,
                "subscription_expires_at": user.subscription_expires_at.isoformat() if user.subscription_expires_at else None,
            }
        }

    @app.post("/auth/login")
    async def email_login(req: EmailLoginRequest, db: AsyncSession = Depends(get_database)):
        """이메일/패스워드 로그인"""
        if db is None:
            raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")

        email = req.email.strip().lower()

        from sqlalchemy import select
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not user.password_hash:
            raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 맞지 않아요")

        if not bcrypt.checkpw(req.password.encode("utf-8"), user.password_hash.encode("utf-8")):
            raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 맞지 않아요")

        user.last_login_at = get_kst_now()
        await db.commit()

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "nickname": user.nickname,
                "profile_image": user.profile_image or "",
                "email": user.email,
                "point_balance": user.point_balance,
                "subscription_tier": user.subscription_tier,
                "subscription_expires_at": user.subscription_expires_at.isoformat() if user.subscription_expires_at else None,
            }
        }
    @app.post("/auth/kakao/callback")
    async def kakao_callback(req: KakaoCallbackRequest, db: AsyncSession = Depends(get_database)):
        """카카오 인가 코드로 토큰 교환, 유저 생성/조회 후 JWT 발급"""
        if db is None:
            raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")

        from sqlalchemy import select

        # 1. 카카오 토큰 교환
        kakao_tokens = await exchange_kakao_code(req.code)
        kakao_access_token = kakao_tokens.get("access_token")
        if not kakao_access_token:
            raise HTTPException(status_code=400, detail="카카오 토큰 교환 실패")

        # 2. 카카오 유저 정보 조회
        kakao_user = await get_kakao_user_info(kakao_access_token)
        kakao_id = kakao_user.get("id")
        if not kakao_id:
            raise HTTPException(status_code=400, detail="카카오 유저 정보 조회 실패")

        nickname = kakao_user.get("properties", {}).get("nickname", "")
        profile_image = kakao_user.get("properties", {}).get("profile_image", "")
        email = kakao_user.get("kakao_account", {}).get("email", "")

        # 3. 유저 생성 또는 조회
        result = await db.execute(select(User).where(User.kakao_id == kakao_id))
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                kakao_id=kakao_id,
                nickname=nickname,
                profile_image=profile_image,
                email=email,
                point_balance=0,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            user.nickname = nickname
            user.profile_image = profile_image
            user.last_login_at = get_kst_today()
            if email:
                user.email = email
            await db.commit()

        # 4. JWT 발급
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "nickname": user.nickname,
                "profile_image": user.profile_image,
                "point_balance": user.point_balance,
                "subscription_tier": user.subscription_tier,
                "subscription_expires_at": user.subscription_expires_at.isoformat() if user.subscription_expires_at else None,
            }
        }

    @app.get("/auth/me")
    async def auth_me(request: Request, db: AsyncSession = Depends(get_database)):
        """JWT 검증 후 유저 정보와 포인트 잔액 반환"""
        user_id = await require_user_id(request)
        if db is None:
            raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")

        from sqlalchemy import select
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="유저를 찾을 수 없어요")

        return {
            "id": user.id,
            "nickname": user.nickname,
            "profile_image": user.profile_image,
            "email": user.email,
            "point_balance": user.point_balance,
            "subscription_tier": user.subscription_tier,
            "subscription_expires_at": user.subscription_expires_at.isoformat() if user.subscription_expires_at else None,
        }

    @app.post("/auth/link-session")
    async def auth_link_session(req: LinkSessionRequest, request: Request, db: AsyncSession = Depends(get_database)):
        """기존 익명 세션을 로그인 유저에 연결"""
        user_id = await require_user_id(request)
        if db is None:
            raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")

        from sqlalchemy import select, update

        # 이미 연결되어 있는지 확인
        result = await db.execute(
            select(UserAuthSession).where(
                UserAuthSession.user_id == user_id,
                UserAuthSession.session_id == req.session_id
            )
        )
        if result.scalar_one_or_none() is None:
            link = UserAuthSession(user_id=user_id, session_id=req.session_id)
            db.add(link)

        # 해당 세션의 리딩들도 유저에 연결
        await db.execute(
            update(TarotReading)
            .where(TarotReading.session_id == req.session_id, TarotReading.user_id == None)
            .values(user_id=user_id)
        )

        await db.commit()
        return {"status": "linked"}

    @app.post("/auth/logout")
    async def auth_logout():
        """로그아웃 (클라이언트에서 토큰 삭제)"""
        return {"status": "logged_out"}

    # Points
    try:
        from points import (
            get_point_balance, consume_points, grant_points,
            get_point_history, get_point_products, get_point_costs, get_feature_cost
        )
        POINTS_AVAILABLE = True
    except Exception as e:
        print(f"⚠️ Points 모듈 로드 실패: {e}")
        POINTS_AVAILABLE = False

    if POINTS_AVAILABLE:
        @app.get("/points/balance")
        async def points_balance(request: Request, db: AsyncSession = Depends(get_database)):
            """포인트 잔액 조회"""
            user_id = await require_user_id(request)
            if db is None:
                raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")
            balance = await get_point_balance(user_id, db)
            return {"balance": balance}

        @app.get("/points/history")
        async def points_history(request: Request, limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_database)):
            """포인트 사용/충전 내역"""
            user_id = await require_user_id(request)
            if db is None:
                raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")
            records = await get_point_history(user_id, db, limit, offset)
            return {
                "history": [
                    {
                        "id": r.id,
                        "usage_type": r.usage_type,
                        "amount": r.amount,
                        "balance_after": r.balance_after,
                        "description": r.description,
                        "created_at": r.created_at.isoformat() if r.created_at else None,
                    }
                    for r in records
                ]
            }

        @app.get("/points/products")
        async def points_products(db: AsyncSession = Depends(get_database)):
            """포인트 충전 상품 목록 (공개)"""
            if db is None:
                return {"products": []}
            products = await get_point_products(db)
            return {
                "products": [
                    {
                        "code": p.code,
                        "name": p.name,
                        "points": p.points,
                        "price": p.price,
                        "bonus_points": p.bonus_points,
                        "description": p.description,
                        "is_popular": p.is_popular,
                    }
                    for p in products
                ]
            }

        @app.get("/points/costs")
        async def points_costs(db: AsyncSession = Depends(get_database)):
            """기능별 포인트 비용 (공개)"""
            if db is None:
                return {"costs": []}
            costs = await get_point_costs(db)
            return {
                "costs": [
                    {
                        "feature_code": c.feature_code,
                        "name": c.name,
                        "cost": c.cost,
                        "description": c.description,
                    }
                    for c in costs
                ]
            }

    # 리딩 히스토리
    @app.get("/user/readings")
    async def user_readings(request: Request, limit: int = 20, offset: int = 0, saved_only: bool = False, favorites_only: bool = False, db: AsyncSession = Depends(get_database)):
        """로그인 유저의 리딩 히스토리"""
        user_id = await require_user_id(request)
        if db is None:
            raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")

        from sqlalchemy import select
        query = select(TarotReading).where(TarotReading.user_id == user_id)
        if saved_only:
            query = query.where(TarotReading.is_saved == True)
        if favorites_only:
            query = query.where(TarotReading.is_favorite == True)
        query = query.order_by(TarotReading.timestamp.desc()).limit(limit).offset(offset)
        result = await db.execute(query)
        readings = result.scalars().all()

        enc = get_encryption()
        items = []
        for r in readings:
            try:
                question = enc.decrypt_text(r.question) if r.question else ""
            except Exception as e:
                print(f"⚠️ 질문 복호화 실패 (id={r.id}): {e}")
                question = r.question or ""

            # 카드 데이터 복호화
            card_names = []
            if r.selected_cards:
                try:
                    cards_data = enc.decrypt_json(r.selected_cards)
                    if isinstance(cards_data, str):
                        cards_data = json.loads(cards_data)
                    if isinstance(cards_data, list):
                        card_names = cards_data
                except Exception as e:
                    print(f"⚠️ 카드 복호화 실패 (id={r.id}): {e}")
                    try:
                        cards_data = json.loads(r.selected_cards)
                        if isinstance(cards_data, list):
                            card_names = cards_data
                    except Exception as e2:
                        print(f"⚠️ 카드 JSON 파싱 실패 (id={r.id}): {e2}")

            items.append({
                "id": r.id,
                "question": question[:100],
                "reading_type": r.reading_type or "basic",
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                "is_favorite": r.is_favorite or False,
                "is_saved": r.is_saved or False,
                "cards": card_names,
            })
        return {"readings": items}

    @app.get("/user/readings/{reading_id}")
    async def user_reading_detail(reading_id: int, request: Request, db: AsyncSession = Depends(get_database)):
        """단일 리딩 상세 조회"""
        user_id = await require_user_id(request)
        if db is None:
            raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")

        from sqlalchemy import select
        result = await db.execute(
            select(TarotReading).where(
                TarotReading.id == reading_id,
                TarotReading.user_id == user_id
            )
        )
        reading = result.scalar_one_or_none()
        if not reading:
            raise HTTPException(status_code=404, detail="리딩을 찾을 수 없어요")

        enc = get_encryption()

        try:
            question = enc.decrypt_text(reading.question) if reading.question else ""
        except Exception as e:
            print(f"⚠️ 리딩 상세 질문 복호화 실패 (id={reading.id}): {e}")
            question = reading.question or ""

        try:
            ai_response = enc.decrypt_text(reading.ai_response) if reading.ai_response else ""
        except Exception as e:
            print(f"⚠️ 리딩 상세 응답 복호화 실패 (id={reading.id}): {e}")
            ai_response = reading.ai_response or ""

        cards = []
        if reading.selected_cards:
            try:
                cards = enc.decrypt_json(reading.selected_cards)
                if isinstance(cards, str):
                    cards = json.loads(cards)
            except Exception as e:
                print(f"⚠️ 리딩 상세 카드 복호화 실패 (id={reading.id}): {e}")
                try:
                    cards = json.loads(reading.selected_cards)
                except Exception as e2:
                    print(f"⚠️ 리딩 상세 카드 JSON 파싱 실패 (id={reading.id}): {e2}")
                    cards = []

        return {
            "id": reading.id,
            "question": question,
            "cards": cards,
            "ai_response": ai_response,
            "reading_type": reading.reading_type or "basic",
            "timestamp": reading.timestamp.isoformat() if reading.timestamp else None,
            "is_saved": reading.is_saved or False,
            "is_favorite": reading.is_favorite or False,
        }

    @app.post("/user/readings/{reading_id}/favorite")
    async def toggle_favorite(reading_id: int, request: Request, db: AsyncSession = Depends(get_database)):
        """리딩 즐겨찾기 토글"""
        user_id = await require_user_id(request)
        if db is None:
            raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")

        from sqlalchemy import select, update
        result = await db.execute(
            select(TarotReading).where(
                TarotReading.id == reading_id,
                TarotReading.user_id == user_id
            )
        )
        reading = result.scalar_one_or_none()
        if not reading:
            raise HTTPException(status_code=404, detail="리딩을 찾을 수 없어요")

        reading.is_favorite = not (reading.is_favorite or False)
        await db.commit()
        return {"is_favorite": reading.is_favorite}

    # Payments (토스페이먼츠)
    try:
        from payments import create_payment_order, confirm_payment, cancel_payment
        PAYMENTS_AVAILABLE = True
    except Exception as e:
        print(f"⚠️ Payments 모듈 로드 실패: {e}")
        PAYMENTS_AVAILABLE = False

    class CreateOrderRequest(BaseModel):
        product_code: str

    class ConfirmPaymentRequest(BaseModel):
        payment_key: str
        order_id: str
        amount: int

    if PAYMENTS_AVAILABLE:
        @app.post("/payments/order")
        async def payments_create_order(req: CreateOrderRequest, request: Request, db: AsyncSession = Depends(get_database)):
            """포인트 충전 주문 생성"""
            user_id = await require_user_id(request)
            if db is None:
                raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")
            return await create_payment_order(user_id, req.product_code, db)

        @app.post("/payments/confirm")
        async def payments_confirm(req: ConfirmPaymentRequest, db: AsyncSession = Depends(get_database)):
            """토스 결제 승인 후 포인트 지급"""
            if db is None:
                raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")
            result = await confirm_payment(req.payment_key, req.order_id, req.amount, db)
            return result

        @app.post("/payments/webhook")
        async def payments_webhook(request: Request, db: AsyncSession = Depends(get_database)):
            """토스 웹훅 (결제 상태 변경 알림)"""
            body = await request.json()
            print(f"💳 토스 웹훅 수신: {body}")
            return {"status": "ok"}

    @app.get("/auth/kakao-config")
    async def kakao_config():
        """프론트엔드에서 카카오 로그인 URL 생성에 필요한 정보"""
        return {
            "rest_api_key": KAKAO_REST_API_KEY,
            "redirect_uri": KAKAO_REDIRECT_URI,
        }


# Subscription
try:
    from subscription import (
        get_subscription_plans, get_subscription_status,
        create_subscription_order, confirm_subscription
    )
    SUBSCRIPTION_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Subscription 모듈 로드 실패: {e}")
    SUBSCRIPTION_AVAILABLE = False

if SUBSCRIPTION_AVAILABLE and AUTH_AVAILABLE:
    @app.get("/subscription/plans")
    async def subscription_plans(db: AsyncSession = Depends(get_database)):
        """구독 상품 목록"""
        if db is None:
            raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")
        return await get_subscription_plans(db)

    @app.get("/subscription/status")
    async def subscription_status(request: Request, db: AsyncSession = Depends(get_database)):
        """현재 유저의 구독 상태"""
        user_id = await require_user_id(request)
        if db is None:
            raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")
        return await get_subscription_status(user_id, db)

    class SubscriptionOrderRequest(BaseModel):
        plan_code: str

    @app.post("/subscription/order")
    async def subscription_order(req: SubscriptionOrderRequest, request: Request, db: AsyncSession = Depends(get_database)):
        """구독 결제 주문 생성"""
        user_id = await require_user_id(request)
        if db is None:
            raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")
        return await create_subscription_order(user_id, req.plan_code, db)

    class SubscriptionConfirmRequest(BaseModel):
        payment_key: str
        order_id: str
        amount: int

    @app.post("/subscription/confirm")
    async def subscription_confirm(req: SubscriptionConfirmRequest, db: AsyncSession = Depends(get_database)):
        """구독 결제 승인"""
        if db is None:
            raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")
        return await confirm_subscription(req.payment_key, req.order_id, req.amount, db)


# Rewarded ad
if AUTH_AVAILABLE and DATABASE_AVAILABLE:
    class RewardedAdCompleteRequest(BaseModel):
        session_id: str

    @app.post("/api/rewarded-ad/complete")
    async def rewarded_ad_complete(req: RewardedAdCompleteRequest, request: Request, db: AsyncSession = Depends(get_database)):
        """보상형 광고 시청 완료 시 리딩 1회 추가 (하루 1회)"""
        if db is None:
            raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")

        from sqlalchemy import select, func
        from database import RewardedAdLog, DailyUsage

        user_id = await get_current_user_id(request)
        today = get_kst_today()

        # 일일 1회 제한 체크
        existing = await db.execute(
            select(func.count()).select_from(RewardedAdLog).where(
                RewardedAdLog.session_id == req.session_id,
                RewardedAdLog.ad_date == today
            )
        )
        count = existing.scalar()
        if count and count >= 1:
            raise HTTPException(status_code=429, detail="오늘은 이미 보상형 광고를 시청했어요")

        # 로그 기록
        log = RewardedAdLog(
            session_id=req.session_id,
            user_id=user_id,
            ad_date=today,
        )
        db.add(log)

        # daily_usage에서 reading_count 1 감소 (= 1회 추가 효과)
        result = await db.execute(
            select(DailyUsage).where(
                DailyUsage.session_id == req.session_id,
                DailyUsage.usage_date == today
            )
        )
        usage = result.scalar_one_or_none()
        if usage and usage.reading_count > 0:
            usage.reading_count -= 1

        await db.commit()

        return {"message": "리딩 1회가 추가되었어요!", "bonus_readings": 1}


@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    if DATABASE_AVAILABLE:
        try:
            await create_tables()
        except Exception as e:
            # 데이터베이스 없이 실행
            print(f"⚠️ DB 테이블 생성 실패: {e}")

    # 카드 데이터, 스프레드, 라우팅, RAG, 암호화를 쓸 수 있는 상태인지 점검.
    # 컴포넌트 실패를 try/except로 삼키고 계속 도는 구조라 여기서 확인하지 않으면 아무도 모른다.
    try:
        from selfcheck import run_selfcheck
        await run_selfcheck()
    except Exception as e:
        print(f"⚠️ 자체 점검 실행 실패: {e}")


@app.get("/selfcheck")
async def selfcheck_endpoint(refresh: bool = False):
    """컴포넌트 점검 결과. refresh=true면 다시 실행"""
    from selfcheck import LAST_RESULT, run_selfcheck
    if refresh or not LAST_RESULT:
        return await run_selfcheck(verbose=False)
    return LAST_RESULT

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
