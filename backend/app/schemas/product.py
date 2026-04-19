from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class ProductListItem(BaseModel):
    product_id: int
    name: str
    description: Optional[str]
    current_stock: int
    unit_price: float
    unit: str
    warehouse: str
    category: str
    low_stock_threshold: int
    expiry_date: Optional[date]
    expiry_status: str
    manufactured_date: Optional[date]
    batch_number: Optional[str]


class ProductListResponse(BaseModel):
    items: list[ProductListItem]
    page: int
    page_size: int
    total: int


class ProductWriteRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: Optional[str] = None
    current_stock: int = Field(ge=0)
    unit_price: float = Field(ge=0)
    unit: str = Field(min_length=1, max_length=30)
    warehouse_id: Optional[int] = None
    category_id: Optional[int] = None
    low_stock_threshold: int = Field(default=10, ge=0)
    expiry_date: Optional[date] = None
    manufactured_date: Optional[date] = None
    batch_number: Optional[str] = Field(default=None, max_length=100)


class ProductMutationResponse(BaseModel):
    success: bool
    message: str
    product_id: Optional[int] = None
