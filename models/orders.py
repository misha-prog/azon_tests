from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class OrderItemResponse(BaseModel):
    product_id: UUID
    product_name: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal


class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    total_amount: Decimal
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime


class OrdersPage(BaseModel):
    items: list[OrderResponse]
    total: int
    page: int
    size: int
    pages: int