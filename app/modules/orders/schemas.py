from datetime import datetime
from pydantic import BaseModel, ConfigDict
from .models import OrderStatus


class OrderCreate(BaseModel):
    item: str


class OrderUpdate(BaseModel):
    """Partial update schema for orders. Only provided fields are applied."""
    item: str | None = None
    status: OrderStatus | None = None

    model_config = ConfigDict(extra="forbid")


class OrderRead(BaseModel):
    id: int
    user_id: int
    item: str
    status: OrderStatus
    delivered_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedOrders(BaseModel):
    items: list[OrderRead]
    total: int
    page: int
    page_size: int
