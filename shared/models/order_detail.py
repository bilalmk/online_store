from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid
from fastapi import File
from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy import DECIMAL, Float


class BaseOrderDetail(SQLModel):
    __tablename__ = "order_detail"  # type: ignore
    order_guid:Optional[str] = Field(default=None)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(
        sa_column=Column(DECIMAL(precision=10, scale=2), nullable=False)
    )
    discount: Decimal = Field(
        sa_column=Column(DECIMAL(precision=10, scale=2), nullable=False)
    )
    total_price: Decimal = Field(
        sa_column=Column(DECIMAL(precision=10, scale=2), nullable=False)
    )
    update_date: datetime = Field(default=datetime.utcnow())
    create_date: datetime = Field(default=datetime.utcnow())
    status: int = Field(default=1, gt=0, lt=100)

    def calculate_total_price(self):
        if self.discount is None:
            self.discount = 0.0  # type: ignore
        self.total_price = (self.unit_price * self.quantity) - self.discount


class OrderDetail(BaseOrderDetail, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(..., gt=0)


class DBOrderDetail(BaseOrderDetail):
    id:int
    order_id: int

class CreateOrderDetail(BaseOrderDetail):
    order_id: Optional[int] = Field(default=None, gt=0)