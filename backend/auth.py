# -*- coding: utf-8 -*-
import os
import jwt
import httpx
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, Request
from database import get_kst_now

# JWT 설정
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY 또는 SECRET_KEY 환경변수가 설정되지 않았습니다. 서버를 시작할 수 없습니다.")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_HOURS = 24
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 30

# 카카오 OAuth 설정
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY", "")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI", "https://serapina.kr/auth/kakao/callback")


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=JWT_ACCESS_TOKEN_EXPIRE_HOURS))
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었어요")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰이에요")


def get_user_id_from_token(token: str) -> int:
    payload = decode_token(token)
    return int(payload["sub"])


async def get_current_user_id(request: Request) -> Optional[int]:
    """요청에서 유저 ID 추출. 로그인 안 했으면 None 반환 (비로그인 허용)"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1]
    try:
        return get_user_id_from_token(token)
    except HTTPException:
        return None


async def require_user_id(request: Request) -> int:
    """요청에서 유저 ID 추출. 로그인 필수."""
    user_id = await get_current_user_id(request)
    if user_id is None:
        raise HTTPException(status_code=401, detail="로그인이 필요해요")
    return user_id


async def exchange_kakao_code(code: str) -> dict:
    """카카오 인가 코드로 토큰 교환"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": KAKAO_REST_API_KEY,
                "redirect_uri": KAKAO_REDIRECT_URI,
                "code": code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="카카오 인증에 실패했어요")
        return response.json()


async def get_kakao_user_info(access_token: str) -> dict:
    """카카오 액세스 토큰으로 유저 정보 조회"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="카카오 유저 정보를 가져올 수 없어요")
        return response.json()
