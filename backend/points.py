# -*- coding: utf-8 -*-
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
from database import User, PointUsage, PointProduct, PointCost, PointCharge, get_kst_now
from fastapi import HTTPException


async def get_point_balance(user_id: int, db: AsyncSession) -> int:
    """유저 포인트 잔액 조회"""
    result = await db.execute(select(User.point_balance).where(User.id == user_id))
    balance = result.scalar_one_or_none()
    if balance is None:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없어요")
    return balance


async def consume_points(
    user_id: int,
    amount: int,
    usage_type: str,
    db: AsyncSession,
    reading_id: int = None,
    description: str = "",
) -> int:
    """
    포인트 차감 (원자적 트랜잭션)
    Returns: 차감 후 잔액
    """
    # SELECT ... FOR UPDATE로 동시 접근 방지
    result = await db.execute(
        text("SELECT point_balance FROM users WHERE id = :uid FOR UPDATE"),
        {"uid": user_id}
    )
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없어요")

    current_balance = row[0]
    if current_balance < amount:
        raise HTTPException(
            status_code=402,
            detail={
                "message": "포인트가 부족해요",
                "current_balance": current_balance,
                "required": amount,
            }
        )

    new_balance = current_balance - amount

    await db.execute(
        update(User).where(User.id == user_id).values(point_balance=new_balance)
    )

    # 사용 기록 저장
    usage = PointUsage(
        user_id=user_id,
        usage_type=usage_type,
        amount=amount,
        balance_after=new_balance,
        reading_id=reading_id,
        description=description,
    )
    db.add(usage)
    await db.commit()

    return new_balance


async def grant_points(
    user_id: int,
    amount: int,
    db: AsyncSession,
    charge_id: int = None,
    description: str = "포인트 충전",
) -> int:
    """
    포인트 지급 (원자적 트랜잭션)
    Returns: 지급 후 잔액
    """
    result = await db.execute(
        text("SELECT point_balance FROM users WHERE id = :uid FOR UPDATE"),
        {"uid": user_id}
    )
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없어요")

    new_balance = row[0] + amount

    await db.execute(
        update(User).where(User.id == user_id).values(point_balance=new_balance)
    )

    usage = PointUsage(
        user_id=user_id,
        usage_type="charge",
        amount=amount,
        balance_after=new_balance,
        charge_id=charge_id,
        description=description,
    )
    db.add(usage)
    await db.commit()

    return new_balance


async def get_point_history(user_id: int, db: AsyncSession, limit: int = 20, offset: int = 0):
    """포인트 사용/충전 내역 조회"""
    result = await db.execute(
        select(PointUsage)
        .where(PointUsage.user_id == user_id)
        .order_by(PointUsage.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def get_point_products(db: AsyncSession):
    """활성 포인트 상품 목록"""
    result = await db.execute(
        select(PointProduct)
        .where(PointProduct.is_active == True)
        .order_by(PointProduct.sort_order)
    )
    return result.scalars().all()


async def get_point_costs(db: AsyncSession):
    """기능별 포인트 비용 목록"""
    result = await db.execute(
        select(PointCost).where(PointCost.is_active == True)
    )
    return result.scalars().all()


async def get_feature_cost(feature_code: str, db: AsyncSession) -> int:
    """특정 기능의 포인트 비용 조회"""
    result = await db.execute(
        select(PointCost.cost).where(
            PointCost.feature_code == feature_code,
            PointCost.is_active == True
        )
    )
    cost = result.scalar_one_or_none()
    if cost is None:
        # 기본 비용 (DB에 없을 때)
        defaults = {
            "extra_reading": 20,
            "premium_reading": 30,
            "extra_question": 10,
            "special_spread": 50,
        }
        return defaults.get(feature_code, 20)
    return cost
