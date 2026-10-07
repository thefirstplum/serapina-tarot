# -*- coding: utf-8 -*-
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Date, JSON, BigInteger, Float, ForeignKey
from datetime import datetime, timezone, timedelta, date
from dotenv import load_dotenv

# 한국 표준시 (KST) 타임존 정의
KST = timezone(timedelta(hours=9))

def get_kst_now():
    """한국 표준시 현재 시간을 반환"""
    return datetime.now(KST)

def get_kst_today():
    """한국 표준시 기준 오늘 날짜를 반환"""
    return datetime.now(KST).date()

load_dotenv()

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+aiomysql://tarot_user:tarot_pass@localhost:3306/tarot_chat"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,  # 연결 재사용 전 ping 테스트
    pool_recycle=1800,  # 30분마다 연결 재생성
)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# Database Models
class TarotSession(Base):
    __tablename__ = "tarot_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True)
    user_agent = Column(Text)
    created_at = Column(DateTime, default=get_kst_now)
    updated_at = Column(DateTime, default=get_kst_now, onupdate=get_kst_now)

class TarotReading(Base):
    __tablename__ = "tarot_readings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    user_id = Column(Integer, index=True, nullable=True)  # 로그인 유저 연결 (nullable: 익명 허용)
    question = Column(Text)
    selected_cards = Column(Text)  # JSON string of selected cards
    ai_response = Column(Text)
    reading_type = Column(String(50), default='basic')  # basic, premium, special_spread
    timestamp = Column(DateTime, default=get_kst_now)
    is_saved = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)  # 즐겨찾기

class UserRating(Base):
    """평점 피드백 테이블"""
    __tablename__ = "user_ratings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    reading_id = Column(Integer)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    categories = Column(JSON)  # 선택한 카테고리 배열
    comment = Column(Text)  # 추가 코멘트
    contact = Column(String(255))  # 연락처
    created_at = Column(DateTime, default=get_kst_now)

class UserFeedback(Base):
    """일반 피드백 테이블 (레거시, 현재는 사용하지 않음)"""
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    reading_id = Column(Integer)
    rating = Column(Integer)  # 1-5 stars
    feedback_text = Column(Text)
    timestamp = Column(DateTime, default=get_kst_now)

class DailyUsage(Base):
    __tablename__ = "daily_usage"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    usage_date = Column(Date, index=True)  # 사용 날짜 (YYYY-MM-DD)
    reading_count = Column(Integer, default=0)  # 하루 동안의 타로 리딩 횟수
    created_at = Column(DateTime, default=get_kst_now)
    updated_at = Column(DateTime, default=get_kst_now, onupdate=get_kst_now)

class AdImpression(Base):
    """광고 노출 추적 테이블"""
    __tablename__ = "ad_impressions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    ad_type = Column(String(50))  # 'display', 'interstitial', 'rewarded' 등
    ad_placement = Column(String(100))  # 'chat', 'card_selection', 'daily_limit' 등
    impression_date = Column(Date, index=True)  # 노출 날짜
    timestamp = Column(DateTime, default=get_kst_now)

class AdClick(Base):
    """광고 클릭 추적 테이블"""
    __tablename__ = "ad_clicks"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    ad_type = Column(String(50))
    ad_placement = Column(String(100))
    click_date = Column(Date, index=True)  # 클릭 날짜
    timestamp = Column(DateTime, default=get_kst_now)

class BlogPost(Base):
    """블로그 포스트 테이블"""
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(50), index=True)  # 연애, 우정, 진로, 가족, 학업, 학교, 자기계발
    excerpt = Column(Text)  # 요약
    situation = Column(Text)  # 고민 상황
    cards = Column(JSON)  # [{"id": "cups02", "name": "컵 2", "position": "정방향"}, ...]
    interpretations = Column(JSON)  # ["<strong>과거 - 컵 2:</strong> ...", ...]
    advice = Column(Text)  # 세라피나의 조언
    tags = Column(JSON)  # ["짝사랑", "고백", "학교"]
    recommended_mbti = Column(JSON)  # 이 글과 잘 맞는 MBTI, 예: ["INFP", "ISFP"]
    gradient = Column(String(255))  # CSS gradient
    emoji = Column(String(10))
    published = Column(Boolean, default=True, index=True)  # 공개 여부
    view_count = Column(Integer, default=0)  # 조회수
    created_at = Column(DateTime, default=get_kst_now)
    updated_at = Column(DateTime, default=get_kst_now, onupdate=get_kst_now)
    published_at = Column(DateTime, default=get_kst_now)  # 게시 날짜

class UserContact(Base):
    """문의하기 테이블"""
    __tablename__ = "user_contacts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    contact_type = Column(String(50), nullable=False)  # 문의 유형
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)  # 문의 내용
    status = Column(String(20), default='pending')  # 처리 상태
    created_at = Column(DateTime, default=get_kst_now)
    updated_at = Column(DateTime, default=get_kst_now, onupdate=get_kst_now)

# 유저 / 포인트 / 결제

class User(Base):
    """소셜 로그인 + 이메일 유저"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    kakao_id = Column(BigInteger, unique=True, index=True, nullable=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    password_hash = Column(String(255), nullable=True)
    nickname = Column(String(100))
    profile_image = Column(String(500))
    point_balance = Column(Integer, default=0, nullable=False)
    subscription_tier = Column(String(20), nullable=True)  # 'monthly', 'yearly'
    subscription_expires_at = Column(DateTime, nullable=True)
    subscription_auto_renew = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_kst_now)
    updated_at = Column(DateTime, default=get_kst_now, onupdate=get_kst_now)
    last_login_at = Column(DateTime, default=get_kst_now)


class UserAuthSession(Base):
    """유저와 타로 세션 매핑"""
    __tablename__ = "user_auth_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    session_id = Column(String(255), index=True, nullable=False)  # 기존 tarot_sessions.session_id
    created_at = Column(DateTime, default=get_kst_now)


class PointProduct(Base):
    """포인트 충전 상품"""
    __tablename__ = "point_products"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)  # 예: 'basic_100', 'popular_300'
    name = Column(String(100), nullable=False)  # 예: '기본 패키지'
    points = Column(Integer, nullable=False)  # 지급 포인트
    price = Column(Integer, nullable=False)  # 가격 (원)
    bonus_points = Column(Integer, default=0)  # 보너스 포인트
    description = Column(String(255))
    is_popular = Column(Boolean, default=False)  # 인기 상품 표시
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=get_kst_now)


class PointCost(Base):
    """기능별 포인트 비용 설정"""
    __tablename__ = "point_costs"

    id = Column(Integer, primary_key=True, index=True)
    feature_code = Column(String(50), unique=True, nullable=False)  # 예: 'premium_reading', 'extra_reading'
    name = Column(String(100), nullable=False)
    cost = Column(Integer, nullable=False)  # 필요 포인트
    description = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_kst_now)


class PointCharge(Base):
    """토스 결제 기록"""
    __tablename__ = "point_charges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    product_code = Column(String(50), nullable=False)  # point_products.code
    order_id = Column(String(100), unique=True, nullable=False)  # 토스 주문 ID
    payment_key = Column(String(200), nullable=True)  # 토스 결제 키 (승인 후)
    amount = Column(Integer, nullable=False)  # 결제 금액 (원)
    points_granted = Column(Integer, nullable=False)  # 지급 포인트 (상품 포인트 + 보너스)
    status = Column(String(20), default='pending', index=True)  # pending, confirmed, cancelled, failed
    created_at = Column(DateTime, default=get_kst_now)
    confirmed_at = Column(DateTime, nullable=True)


class PointUsage(Base):
    """포인트 사용 기록"""
    __tablename__ = "point_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    usage_type = Column(String(50), nullable=False)  # extra_reading, premium_reading, extra_question, special_spread
    amount = Column(Integer, nullable=False)  # 사용 포인트 (양수)
    balance_after = Column(Integer, nullable=False)  # 사용 후 잔액
    reading_id = Column(Integer, nullable=True)  # 관련 리딩 ID
    charge_id = Column(Integer, nullable=True)  # 충전 관련 ID (포인트 지급 시)
    description = Column(String(255))
    created_at = Column(DateTime, default=get_kst_now)


class SubscriptionPlan(Base):
    """구독 상품"""
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)  # 'monthly', 'yearly'
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)  # 원
    original_price = Column(Integer, nullable=True)  # 할인 전 가격
    duration_days = Column(Integer, nullable=False)  # 30 or 365
    description = Column(String(255))
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=get_kst_now)


class SubscriptionPayment(Base):
    """구독 결제 기록"""
    __tablename__ = "subscription_payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    plan_code = Column(String(50), nullable=False)
    order_id = Column(String(100), unique=True, nullable=False)
    payment_key = Column(String(200), nullable=True)
    amount = Column(Integer, nullable=False)
    status = Column(String(20), default='pending', index=True)  # pending, confirmed, cancelled, failed
    created_at = Column(DateTime, default=get_kst_now)
    confirmed_at = Column(DateTime, nullable=True)


class RewardedAdLog(Base):
    """보상형 광고 시청 기록"""
    __tablename__ = "rewarded_ad_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    user_id = Column(Integer, nullable=True, index=True)
    ad_date = Column(Date, index=True)
    created_at = Column(DateTime, default=get_kst_now)


# Database dependency
async def get_database():
    session = None
    try:
        session = AsyncSessionLocal()
        yield session
    except Exception as e:
        import traceback
        print(f"Database connection failed: {type(e).__name__}: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        yield None
    finally:
        if session:
            try:
                await session.close()
            except Exception as close_error:
                print(f"Error closing DB session: {close_error}")

# Create tables
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)