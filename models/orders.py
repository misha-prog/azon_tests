from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
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

class CardBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    card_number: str = Field(pattern=r"^\d{16}$")
    card_holder: str = Field(max_length=50)
    exp_month: int = Field(le=12, ge=1)
    exp_year: int = Field(ge=2026, le=2060)
    cvc: str = Field(pattern=r"^\d{3}$")

class PaymentResponse(BaseModel):
    payment_id: UUID
    status: str
    order_status: str