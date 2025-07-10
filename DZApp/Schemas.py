from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SupplierBase(BaseModel):
    Name: str
    Brand: Optional[str] = None
    Contact: Optional[str] = None

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
