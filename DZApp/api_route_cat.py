from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from sqlalchemy.orm import selectinload

from ImprovedPython.DZdict.connect import async_session_factory
from ImprovedPython.DZdict.tables import Product
from ImprovedPython.DZdict.schemas import CategoryResponse, ProductODT, SupplierShort, OrdersStats
from fastapi_cache.decorator import cache

router = APIRouter(prefix="/categories", tags=["Categories"])


async def get_db():
    async with async_session_factory() as session:
        yield session


@router.get("/{category_id}", response_model=List[ProductODT])
@cache(expire=30)
async def get_products_by_category(category_path: str, db: AsyncSession = Depends(get_db)):
    try:
        category = category_path.replace('-', '/')
        # Загружаем продукты с указанной категорией вместе со связанными данными
        result = await db.execute(
            select(Product)
            .where(Product.Category == category)
            .options(
                selectinload(Product.supplier),
                selectinload(Product.orders)
            )
        )
        products = result.scalars().all()

        if not products:
            raise HTTPException(
                status_code=404,
                detail=f"No products found for category: {category}"
            )

        product_list = []
        for product in products:
            # Рассчитываем статистику по заказам
            total_orders = sum(order.Quantity for order in product.orders) if product.orders else 0
            days_on_sale = max(order.DaysOnSale for order in product.orders) if product.orders else 0
            days_with_sales = max(order.DaysWithSales for order in product.orders) if product.orders else 0
            fbo_turnover = sum(order.FBOTurnover for order in product.orders) if product.orders else 0
            fbs_turnover = sum(order.FBSTurnover for order in product.orders) if product.orders else 0
            lost_profit = sum(order.LostProfit for order in product.orders) if product.orders else 0
            lost_profit_percent = sum(order.LostProfitPercent for order in product.orders) / len(product.orders) if product.orders else 0
            search_queries = sum(order.SearchQueries for order in product.orders) if product.orders else 0

            product_odt = ProductODT(
                ID=product.ID,
                Name=product.Name,
                SKU=product.SKU,
                Price=product.Price,
                Category=product.Category,
                Stock=product.Stock,
                ReviewsCount=product.ReviewsCount,
                Supplier=SupplierShort(
                    Name=product.supplier.Name,
                    Brand=product.supplier.Brand
                ),
                OrdersStats=OrdersStats(
                    TotalOrders=total_orders,
                    DaysOnSale=days_on_sale,
                    DaysWithSales=days_with_sales,
                    FBOTurnover=fbo_turnover,
                    FBSTurnover=fbs_turnover,
                    LostProfit=lost_profit,
                    LostProfitPercent=lost_profit_percent,
                    SearchQueries=search_queries
                )
            )
            product_list.append(product_odt)

        return product_list

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )


@router.get("/", response_model=List[CategoryResponse])
@cache(expire=30)
async def get_all_categories(db: AsyncSession = Depends(get_db)):
    try:
        # Получаем все категории с количеством товаров
        stmt = select(
            Product.Category,
            func.count(Product.ID).label("product_count")
        ).group_by(Product.Category)

        result = await db.execute(stmt)
        categories = result.all()

        return [
            CategoryResponse(
                name=category[0],
                product_count=category[1]
            )
            for category in categories
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

@router.get("/products/", response_model=List[int])
@cache(expire=30)
async def get_all_skus(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product.SKU))
    return result.scalars().all()
