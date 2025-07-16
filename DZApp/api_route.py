from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ImprovedPython.DZdict.connect import async_session_factory
from ImprovedPython.DZdict.tables import Supplier
from ImprovedPython.DZdict.schemas import SupplierResponse, SupplierUpdate
from ImprovedPython.DZdict.celery_task import generate_seller_statistics
from ImprovedPython.DZdict.schemas import StatsRequest

from fastapi import BackgroundTasks
from fastapi_cache.decorator import cache
import time


router = APIRouter(prefix="/sellers", tags=["Sellers"])

async def get_db():
    async with async_session_factory() as session:
        yield session

# 1. Получение всех продавцов
@router.get("/", response_model=List[SupplierResponse])
@cache(expire=30)
async def get_all_sellers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supplier))
    sellers = result.scalars().all()
    time.sleep(3)
    return sellers

# 2. Получение продавца по ID
@router.get("/{seller_id}/", response_model=SupplierResponse)
@cache(expire=30)
async def get_seller_by_id(seller_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supplier).where(Supplier.ID == seller_id))
    seller = result.scalars().first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    time.sleep(3)
    return seller

@router.put("/{seller_id}/update", response_model=SupplierResponse)
@cache(expire=30)
async def update_seller(seller_id: int, updated_data: SupplierUpdate,
                        db: AsyncSession = Depends(get_db)):
    seller = await db.get(Supplier, seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Продавец не найден")
    # 2. Обновляем только переданные поля
    update_data = updated_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(seller, field, value)
    # 3. Фиксируем изменения
    await db.commit()
    # 4. Обновляем объект из БД
    await db.refresh(seller)
    time.sleep(3)
    return seller


@router.post("/statistics/")
async def request_statistics(
        request: StatsRequest,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db)):

    # Проверяем, что продавец существует
    result = await db.execute(select(Supplier).where(Supplier.ID == request.seller_id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Seller not found")

    # Добавляем задачу в фоне
    background_tasks.add_task(
    generate_seller_statistics.s(seller_id=request.seller_id, email=request.email).delay)

    return {"message": "Report generation started. You will receive it by email shortly."}
