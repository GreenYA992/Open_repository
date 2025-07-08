from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import Dict, Any
import math


class AsyncDataToPostgresSaver:
    def __init__(self, async_session_factory):
        self.async_session_factory = async_session_factory

    async def save_to_database(self, data: Dict[int, Dict[str, Any]]):
        """Асинхронное сохранение данных"""
        async with self.async_session_factory() as session:
            try:
                for category_id, products in data.items():
                    for product_id, product_data in products.items():
                        await self._process_product(session, product_data)
                await session.commit()

            except SQLAlchemyError:
                await session.rollback()
                raise

    async def _process_product(self, session: AsyncSession,
                               product_data: Dict[str, Any]):
        supplier = await self._get_or_create_supplier(
            session,
            product_data.get("Продавец", "Неизвестный поставщик"),
            product_data.get("Бренд", "Неизвестный бренд"))

        product = await self._get_or_create_product(
            session,
            product_data,
            supplier.ID)

        await self._create_order_record(
            session,
            product_data,
            product.ID,
            supplier.ID)

    async def _get_or_create_supplier(self, session: AsyncSession,
                                      name: str, brand: str):

        from ImprovedPython.DZdict.tables import Supplier

        if isinstance(brand, float) and math.isnan(brand):
            brand = "Неизвестный бренд"
        if isinstance(name, float) and math.isnan(name):
            name = "Неизвестный поставщик"

        result = await session.execute(select(Supplier).where(Supplier.Name == name))
        supplier = result.scalars().first()

        if not supplier:
            supplier = Supplier(
                Name=str(name),
                Brand=str(brand),
                CreatedOn=datetime.now(),
                UpdatedAt=datetime.now())
            session.add(supplier)
            await session.flush()

        return supplier

    async def _get_or_create_product(self, session: AsyncSession,
                                     product_data: Dict[str, Any],
                                     supplier_id: int):

        from ImprovedPython.DZdict.tables import Product

        def clean_value(value, default):
            if isinstance(value, float) and math.isnan(value):
                return default
            return value if value is not None else default

        sku = clean_value(product_data.get("SKU"), 0)

        if not sku:
            raise ValueError("Отсутствует SKU продукта")

        result = await session.execute(select(Product).where(Product.SKU == sku))
        product = result.scalars().first()

        if not product:
            product = Product(
                SKU=int(sku),
                Name=str(clean_value(product_data.get("Название"), "Без названия")),
                Price=float(clean_value(product_data.get("Цена"), 0)),
                Category=str(clean_value(product_data.get("Основная категория"), "Неизвестная категория")),
                SupplierID=supplier_id,
                Stock=int(clean_value(product_data.get("Последние остатки на складах"), 0)),
                ReviewsCount=int(clean_value(product_data.get("Отзывов"), 0)),
                CreatedOn=datetime.now(),
                UpdatedAt=datetime.now())
            session.add(product)
            await session.flush()

        else:
            product.Name = str(clean_value(product_data.get("Название"), product.Name))
            product.Price = float(clean_value(product_data.get("Цена"), product.Price))
            product.Category = str(clean_value(product_data.get("Основная категория"), product.Category))
            product.Stock = int(clean_value(product_data.get("Последние остатки на складах"), product.Stock))
            product.ReviewsCount = int(clean_value(product_data.get("Отзывов"), product.ReviewsCount))
            product.UpdatedAt = datetime.now()

        return product

    async def _create_order_record(self, session: AsyncSession,
                                   product_data: Dict[str, Any],
                                   product_id: int,
                                   supplier_id: int):

        from ImprovedPython.DZdict.tables import Order

        order = Order(
            ProductID=product_id,
            SupplierID=supplier_id,
            Quantity=product_data.get("Кол-во заказов", 0),
            DaysOnSale=product_data.get("Кол-во дней когда артикул был в продаже", 0),
            DaysWithSales=product_data.get("Кол-во дней, когда артикул покупали", 0),
            FBOTurnover=float(product_data.get("Оборот FBO", 0)),
            FBSTurnover=float(product_data.get("Оборот FBS", 0)),
            LostProfit=float(product_data.get("Упущенная выгода", 0)),
            LostProfitPercent=float(product_data.get("Упущенная выгода в процентах", 0)),
            SearchQueries=product_data.get("Поисковых запросов", 0),
            OrderDate=datetime.now())
        session.add(order)
