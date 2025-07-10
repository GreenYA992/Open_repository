from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ImprovedPython.DZdict.connect import async_session_factory
from ImprovedPython.DZdict.tables import Supplier
from ImprovedPython.DZdict.Schemas import SupplierResponse, SupplierUpdate


router = APIRouter(prefix="/sellers", tags=["Sellers"])

async def get_db():
    async with async_session_factory() as session:
        yield session

# 1. Получение всех продавцов
@router.get("/", response_model=List[SupplierResponse])
async def get_all_sellers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supplier))
    sellers = result.scalars().all()
    return sellers

# 2. Получение продавца по ID
@router.get("/{seller_id}/", response_model=SupplierResponse)
async def get_seller_by_id(seller_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supplier).where(Supplier.ID == seller_id))
    seller = result.scalars().first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    return seller

@router.put("/{seller_id}/update", response_model=SupplierResponse)
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
    return seller
