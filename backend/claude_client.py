"""
Claude API Client for Tarot Reading
"""
import os
from dotenv import load_dotenv
from anthropic import Anthropic
from typing import AsyncGenerator, Dict, List, Optional
import json

load_dotenv()

# Claude API 설정
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
CLAUDE_MODEL_LIGHT = os.getenv("CLAUDE_MODEL_LIGHT", "claude-haiku-4-5-20251001")  # Haiku 4.5
CLAUDE_MODEL_HEAVY = os.getenv("CLAUDE_MODEL_HEAVY", "claude-sonnet-4-6")  # Sonnet 4.6

claude_client = None
if CLAUDE_API_KEY:
    claude_client = Anthropic(api_key=CLAUDE_API_KEY)
    print(f"✅ Claude API 초기화 완료")
    print(f"  - Light Model: {CLAUDE_MODEL_LIGHT}")
    print(f"  - Heavy Model: {CLAUDE_MODEL_HEAVY}")
else:
    print("⚠️ CLAUDE_API_KEY가 설정되지 않았습니다.")


async def call_claude_api(
    messages: List[Dict[str, str]],
    system_prompt: str,
    model: str = "light",
    max_tokens: int = 4096,
    temperature: float = 0.7,
    stream: bool = False
) -> AsyncGenerator[str, None] | str:
    """
    Claude 호출. model은 "light"(Haiku) / "heavy"(Sonnet).
    stream=True면 텍스트 청크를 내는 async generator 반환
    """
    if not claude_client:
        raise Exception("Claude API client가 초기화되지 않았습니다. CLAUDE_API_KEY를 확인하세요.")

    model_name = CLAUDE_MODEL_HEAVY if model == "heavy" else CLAUDE_MODEL_LIGHT

    if stream:
        async def stream_response():
            with claude_client.messages.stream(
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    yield text

        return stream_response()
    else:
        message = claude_client.messages.create(
            model=model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=messages
        )

        return message.content[0].text


def get_claude_model_info():
    """Claude 모델 정보 반환"""
    return {
        "light_model": CLAUDE_MODEL_LIGHT,
        "heavy_model": CLAUDE_MODEL_HEAVY,
        "api_initialized": claude_client is not None
    }
