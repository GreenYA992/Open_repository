from fastapi import FastAPI
#from ImprovedPython.DZdict.connect import session_factory
#from ImprovedPython.DZdict.tables import create_table_if_not_exists
from contextlib import asynccontextmanager
from ImprovedPython.DZdict.api_route_sellers import router as seller_router
from ImprovedPython.DZdict.api_route_stat import router as stat_router
from ImprovedPython.DZdict.api_route_cat import router as category_router
from celery import Celery

from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend


app = FastAPI()

"""
@app.on_event("startup")
async def startup():
    #engine = session_factory()
    #create_table_if_not_exists(engine)
    """
celery = Celery('tasks',
                broker='redis://localhost:6379/0',
                include=['ImprovedPython.DZdict.celery_task'])

redis = aioredis.from_url("redis://localhost", encoding='utf8', decode_responses=True)
FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')

app.include_router(category_router, tags=['Categories'], prefix='/categories')
app.include_router(seller_router, tags=['Sellers'], prefix='/sellers')
app.include_router(stat_router, tags=['Statistics'], prefix='/statistics')

@app.get("/")
async def root():
    return {"message": "Sellers API is running. Go to /docs for documentation."}

# Для запуска команда -  celery -A ImprovedPython.DZdict.api_main:celery worker --loglevel=INFO --pool=solo
# Для запуска команда -  python -m uvicorn ImprovedPython.DZdict.api_main:app
