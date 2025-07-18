from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Dict, Any

class SupplierBase(BaseModel):
    Name: str
    Brand: Optional[str] = None
    Contact: Optional[str] = None


class StatsRequest(BaseModel):
    email: EmailStr
    seller_id: int

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    ID: int
    CreatedOn: datetime
    UpdatedAt: datetime

    class Config:
        from_attributes = True  # Работает с ORM (альяс для orm_mode = True)

class SellerWithSalesResponse(SupplierResponse):
    total_products: int
    total_sales: int
    recent_orders: List[Dict[str, Any]]  # или создайте отдельную схему для заказов

    class Config:
        from_attributes = True

""""""

class CategoryResponse(BaseModel):
    name: str
    product_count: int

class SupplierShort(BaseModel):
    Name: str
    Brand: Optional[str]

class OrdersStats(BaseModel):
    TotalOrders: int
    DaysOnSale: int
    DaysWithSales: int
    FBOTurnover: float
    FBSTurnover: float
    LostProfit: float
    LostProfitPercent: float
    SearchQueries: int

class ProductODT(BaseModel):
    ID: int
    Name: str
    SKU: int
    Price: float
    Category: str
    Stock: int
    ReviewsCount: int
    Supplier: SupplierShort
    OrdersStats: OrdersStats

    class Config:
        from_attributes = True
