# -*- coding: utf-8 -*-
import os
import uuid
import base64
import httpx
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import SubscriptionPlan, SubscriptionPayment, User, get_kst_now, KST
from fastapi import HTTPException

TOSS_SECRET_KEY = os.getenv("TOSS_SECRET_KEY", "")
TOSS_API_URL = "https://api.tosspayments.com/v1/payments"


def _toss_auth_header() -> dict:
    encoded = base64.b64encode(f"{TOSS_SECRET_KEY}:".encode()).decode()
    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json",
    }


async def get_subscription_plans(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(SubscriptionPlan)
        .where(SubscriptionPlan.is_active == True)
        .order_by(SubscriptionPlan.sort_order)
    )
    plans = result.scalars().all()
    return [
        {
            "code": p.code,
            "name": p.name,
            "price": p.price,
            "original_price": p.original_price,
            "duration_days": p.duration_days,
            "description": p.description,
        }
        for p in plans
    ]


async def get_subscription_status(user_id: int, db: AsyncSession) -> dict:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없어요")

    is_active = False
    if user.subscription_tier and user.subscription_expires_at:
        is_active = user.subscription_expires_at > datetime.now(KST)

    return {
        "tier": user.subscription_tier,
        "expires_at": user.subscription_expires_at.isoformat() if user.subscription_expires_at else None,
        "auto_renew": user.subscription_auto_renew,
        "is_active": is_active,
    }


async def create_subscription_order(user_id: int, plan_code: str, db: AsyncSession) -> dict:
    result = await db.execute(
        select(SubscriptionPlan).where(
            SubscriptionPlan.code == plan_code,
            SubscriptionPlan.is_active == True,
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="존재하지 않는 구독 상품이에요")

    order_id = f"SUB-{user_id}-{uuid.uuid4().hex[:12]}"

    payment = SubscriptionPayment(
        user_id=user_id,
        plan_code=plan_code,
        order_id=order_id,
        amount=plan.price,
        status="pending",
    )
    db.add(payment)
    await db.commit()

    return {
        "order_id": order_id,
        "amount": plan.price,
        "product_name": plan.name,
        "plan_code": plan_code,
    }


async def confirm_subscription(
    payment_key: str, order_id: str, amount: int, db: AsyncSession
) -> dict:
    result = await db.execute(
        select(SubscriptionPayment).where(SubscriptionPayment.order_id == order_id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없어요")

    if payment.status != "pending":
        raise HTTPException(status_code=400, detail="이미 처리된 주문이에요")

    if payment.amount != amount:
        payment.status = "failed"
        await db.commit()
        raise HTTPException(status_code=400, detail="결제 금액이 일치하지 않아요")

    if not TOSS_SECRET_KEY:
        raise HTTPException(status_code=503, detail="결제 시스템이 설정되지 않았어요")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{TOSS_API_URL}/confirm",
            headers=_toss_auth_header(),
            json={
                "paymentKey": payment_key,
                "orderId": order_id,
                "amount": amount,
            },
        )

    if response.status_code != 200:
        error_data = response.json()
        payment.status = "failed"
        await db.commit()
        raise HTTPException(
            status_code=400,
            detail=error_data.get("message", "결제 승인에 실패했어요"),
        )

    # 결제 성공 시 구독 활성화
    payment.payment_key = payment_key
    payment.status = "confirmed"
    payment.confirmed_at = get_kst_now()

    plan_result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.code == payment.plan_code)
    )
    plan = plan_result.scalar_one()

    # 유저 구독 업데이트
    user_result = await db.execute(select(User).where(User.id == payment.user_id))
    user = user_result.scalar_one()

    now = get_kst_now()
    # 기존 구독이 남아있으면 거기서 연장
    if user.subscription_expires_at and user.subscription_expires_at > now:
        new_expires = user.subscription_expires_at + timedelta(days=plan.duration_days)
    else:
        new_expires = now + timedelta(days=plan.duration_days)

    user.subscription_tier = payment.plan_code
    user.subscription_expires_at = new_expires
    user.subscription_auto_renew = True

    await db.commit()

    return {
        "status": "confirmed",
        "tier": payment.plan_code,
        "expires_at": new_expires.isoformat(),
    }
