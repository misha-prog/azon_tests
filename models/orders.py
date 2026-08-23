from datetime import date, datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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
    warnings: list[str] = Field(default_factory=list)
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
    card_number: str = Field(pattern=r"^\d{12,19}$")
    card_holder: str = Field(min_length=1, max_length=100)
    exp_month: int = Field(ge=1, le=12)
    exp_year: int = Field(ge=2020, le=2100)
    cvc: str = Field(pattern=r"^\d{3}$")

    @field_validator("card_number")
    @classmethod
    def card_number_must_pass_luhn(cls, card_number: str) -> str:
        digits = [int(digit) for digit in card_number]
        parity = len(digits) % 2
        checksum = 0

        for index, digit in enumerate(digits):
            if index % 2 == parity:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit

        if checksum % 10:
            raise ValueError("card_number failed the Luhn check")
        return card_number

    @model_validator(mode="after")
    def card_must_not_be_expired(self) -> Self:
        today = date.today()
        if (self.exp_year, self.exp_month) < (today.year, today.month):
            raise ValueError("card is expired")
        return self


class PaymentResponse(BaseModel):
    payment_id: UUID
    status: str
    order_status: str


class PaymentBriefResponse(BaseModel):
    id: UUID
    amount: Decimal
    status: str
    card_last4: str
    decline_code: str | None
    created_at: datetime
