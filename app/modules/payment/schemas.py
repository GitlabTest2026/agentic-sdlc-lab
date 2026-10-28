from pydantic import BaseModel, ConfigDict
from .models import InvoiceStatus
from datetime import datetime


class InvoiceCreate(BaseModel):
    order_id: int


class InvoiceRead(BaseModel):
    id: int
    order_id: int
    status: InvoiceStatus
    external_invoice_id: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceRefund(InvoiceRead):
    pass


class InvoicePaid(BaseModel):
    order_id: int
    external_invoice_id: str | None = None


class PaginatedInvoices(BaseModel):
    items: list[InvoiceRead]
    total: int
    page: int
    page_size: int
