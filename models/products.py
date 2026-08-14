from pydantic import BaseModel, Field
from decimal import Decimal
from uuid import UUID
from datetime import datetime

class ProductRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    sku: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9._-]+$")
    description: str = Field(max_length=5000)
    price: Decimal = Field(gt=0, le=1_000_000)
    stock: int = Field(ge=0, le=1_000_000)
    category_id: UUID

class ProductResponse(BaseModel):
    id: UUID
    sku: str
    name: str
    price: Decimal
    stock: int
    rating_avg: float | None
    is_seed: bool
    created_at: datetime
    is_available: bool


class ProductsPage(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    size: int
    pages: int

