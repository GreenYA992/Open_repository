from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ImprovedPython.DZdict.connect import async_session_factory
from ImprovedPython.DZdict.tables import Supplier
from ImprovedPython.DZdict.celery_task import generate_seller_statistics
from ImprovedPython.DZdict.schemas import StatsRequest

from fastapi import BackgroundTasks


router = APIRouter(prefix="/statistics", tags=["Statistics"])

async def get_db():
    async with async_session_factory() as session:
        yield session

@router.post("/")
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
