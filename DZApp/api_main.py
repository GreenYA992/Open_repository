from fastapi import FastAPI
# from ImprovedPython.DZdict.connect import async_session_factory
# from ImprovedPython.DZdict.tables import * # create_table_if_not_exists
from ImprovedPython.DZdict.api_route import router

app = FastAPI()

"""
@app.on_event("startup")
async def startup():
    #engine = async_session_factory()
    await create_table_if_not_exists(engine)
"""

app.include_router(router, tags=['Sellers'], prefix='/sellers')

@app.get("/")
async def root():
    return {"message": "Sellers API is running. Go to /docs for documentation."}

# Для запуска команда -  python -m uvicorn ImprovedPython.DZdict.api_main:app
