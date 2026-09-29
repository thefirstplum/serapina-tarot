# -*- coding: utf-8 -*-
import os
import uuid
import base64
import httpx
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import PointCharge, PointProduct, get_kst_now
from points import grant_points
from fastapi import HTTPException

TOSS_SECRET_KEY = os.getenv("TOSS_SECRET_KEY", "")
TOSS_API_URL = "https://api.tosspayments.com/v1/payments"


def _toss_auth_header() -> dict:
    """토스 API 인증 헤더"""
    encoded = base64.b64encode(f"{TOSS_SECRET_KEY}:".encode()).decode()
    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json",
    }


async def create_payment_order(
    user_id: int,
    product_code: str,
    db: AsyncSession,
) -> dict:
    """
    결제 주문 생성
    Returns: {"order_id": str, "amount": int, "product_name": str, "points": int}
    """
    result = await db.execute(
        select(PointProduct).where(
            PointProduct.code == product_code,
            PointProduct.is_active == True
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="존재하지 않는 상품이에요")

    order_id = f"SERAPINA-{user_id}-{uuid.uuid4().hex[:12]}"
    total_points = product.points + product.bonus_points

    # 주문 기록 생성 (pending 상태)
    charge = PointCharge(
        user_id=user_id,
        product_code=product_code,
        order_id=order_id,
        amount=product.price,
        points_granted=total_points,
        status="pending",
    )
    db.add(charge)
    await db.commit()

    return {
        "order_id": order_id,
        "amount": product.price,
        "product_name": product.name,
        "points": total_points,
    }


async def confirm_payment(
    payment_key: str,
    order_id: str,
    amount: int,
    db: AsyncSession,
) -> dict:
    """
    토스 결제 승인 + 포인트 지급
    Returns: {"status": str, "balance": int}
    """
    result = await db.execute(
        select(PointCharge).where(PointCharge.order_id == order_id)
    )
    charge = result.scalar_one_or_none()
    if not charge:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없어요")

    if charge.status != "pending":
        raise HTTPException(status_code=400, detail="이미 처리된 주문이에요")

    # 금액 대조 (프론트 조작 방지)
    if charge.amount != amount:
        charge.status = "failed"
        await db.commit()
        raise HTTPException(status_code=400, detail="결제 금액이 일치하지 않아요")

    # 토스 결제 승인 API 호출
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
        charge.status = "failed"
        await db.commit()
        raise HTTPException(
            status_code=400,
            detail=error_data.get("message", "결제 승인에 실패했어요"),
        )

    # 결제 성공 시 포인트 지급
    charge.payment_key = payment_key
    charge.status = "confirmed"
    charge.confirmed_at = get_kst_now()
    await db.commit()

    new_balance = await grant_points(
        user_id=charge.user_id,
        amount=charge.points_granted,
        db=db,
        charge_id=charge.id,
        description=f"포인트 충전 ({charge.points_granted}P)",
    )

    return {
        "status": "confirmed",
        "balance": new_balance,
        "points_granted": charge.points_granted,
    }


async def cancel_payment(
    payment_key: str,
    reason: str,
    db: AsyncSession,
) -> dict:
    """결제 취소"""
    result = await db.execute(
        select(PointCharge).where(PointCharge.payment_key == payment_key)
    )
    charge = result.scalar_one_or_none()
    if not charge:
        raise HTTPException(status_code=404, detail="결제를 찾을 수 없어요")

    if charge.status != "confirmed":
        raise HTTPException(status_code=400, detail="취소할 수 없는 상태에요")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{TOSS_API_URL}/{payment_key}/cancel",
            headers=_toss_auth_header(),
            json={"cancelReason": reason},
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="결제 취소에 실패했어요")

    charge.status = "cancelled"
    await db.commit()

    return {"status": "cancelled"}
