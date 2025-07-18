from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy.orm import selectinload
from decimal import Decimal

from ImprovedPython.DZdict.connect import async_session_factory
from ImprovedPython.DZdict.tables import Supplier
from ImprovedPython.DZdict.schemas import SupplierResponse, SupplierUpdate, SellerWithSalesResponse
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

@router.get("/{seller_id}/stats", response_model=SellerWithSalesResponse)
@cache(expire=30)
async def get_seller_stats(seller_id: int, db: AsyncSession = Depends(get_db)):
    # Загружаем продавца вместе со связанными данными
    result = await db.execute(
        select(Supplier)
        .where(Supplier.ID == seller_id)
        .options(
            selectinload(Supplier.products),
            selectinload(Supplier.orders)
        )
    )
    seller = result.scalars().first()

    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")

    # Преобразуем Decimal в float для сериализации
    def convert_decimal(value):
        if isinstance(value, Decimal):
            return float(value)
        return value

    # Считаем статистику
    total_products = len(seller.products)
    total_sales = sum(order.Quantity for order in seller.orders)

    # Формируем список последних заказов (примерно 5 последних)
    recent_orders = []
    for order in sorted(seller.orders, key=lambda x: x.OrderDate, reverse=True)[:5]:
        recent_orders.append({
            "order_id": order.ID,
            "product_id": order.ProductID,
            "product_name": order.product.Name if order.product else "Unknown",
            "quantity": order.Quantity,
            "date": order.OrderDate.isoformat(),
            "turnover": convert_decimal(order.FBOTurnover + order.FBSTurnover)
        })

    # Подготавливаем данные продавца
    seller_data = {
        "ID": seller.ID,
        "Name": seller.Name,
        "Brand": seller.Brand,
        "Contact": seller.Contact,
        "CreatedOn": seller.CreatedOn.isoformat(),
        "UpdatedAt": seller.UpdatedAt.isoformat(),
        "total_products": total_products,
        "total_sales": total_sales,
        "recent_orders": recent_orders
    }

    return seller_data

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
