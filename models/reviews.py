from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime

class ReviewCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rating: int = Field(ge=1, le=5)
    text: str = Field(min_length=1, max_length=2000)


class ReviewUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rating: int | None = Field(None, ge=1, le=5)
    text: str | None = Field(None, min_length=1, max_length=2000)


class ReviewResponse(BaseModel):
    id: UUID
    product_id: UUID
    user_id: UUID
    user_name: str
    rating: int
    text: str
    is_seed: bool
    created_at: datetime
    updated_at: datetime


class ReviewsPage(BaseModel):
    items: list[ReviewResponse]
    total: int
    page: int
    size: int
    pages: int

class StrictReviewResponse(ReviewResponse):
    model_config = ConfigDict(extra="forbid")