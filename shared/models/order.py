from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid
from fastapi import File
from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy import DECIMAL, Float


class BaseOrder(SQLModel):
    __tablename__ = "orders"  # type: ignore
    customer_id: int = Field(..., gt=0)
    total_amount: Decimal = Field(
        sa_column=Column(DECIMAL(precision=10, scale=2), nullable=False)
    )
    order_date: datetime = Field(default=datetime.utcnow())
    shipping_address: str = Field(..., min_length=3, max_length=2000)
    billing_address: str = Field(..., min_length=3, max_length=2000)
    payment_method: str = Field(..., min_length=3, max_length=100)
    payment_status: Optional[str] = Field(
        default="unpaid", min_length=3, max_length=100
    )
    delivery_date: Optional[datetime] = Field(default=None)
    delivery_status: Optional[str] = Field(
        default="pending", min_length=3, max_length=100
    )
    order_status: Optional[str] = Field(default="process", min_length=3, max_length=100)
    guid: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), max_length=40
    )
    created_by: int = Field(..., gt=0)
    created_at: datetime = Field(default=datetime.utcnow())
    status: int = Field(default=1, gt=0, lt=100)

class Order(BaseOrder, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class DBOrder(Order):
    pass


class CreateOrder(BaseOrder):
    pass


class PublicOrder(BaseOrder):
    id: int
    category_name: Optional[str] = None
    brand_name: Optional[str] = None


class UpdateOrder(SQLModel):
    __tablename__ = "orders"  # type: ignore
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    image_name: Optional[str] = None
    status: Optional[int] = None
