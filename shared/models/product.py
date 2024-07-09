from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid
from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy import DECIMAL, Float

class BaseProduct(SQLModel):
    __tablename__ = "products"  # type: ignore
    name: str = Field(..., min_length=3, max_length=2000)
    description: Optional[str] = None
    price: float = Field(
        sa_column=Column(Float, nullable=False)
    )
    # price: DECIMAL = Field(
    #     sa_column=Column(DECIMAL(precision=10, scale=2), nullable=False)
    # )
    stock_quantity: int = Field(..., gt=0)
    category_id: int = Field(..., gt=0)
    brand_id: int = Field(..., gt=0)
    image_name: Optional[str] = Field(default=None, max_length=1000)
    guid: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), max_length=40
    )
    created_by: int = Field(..., gt=0)
    created_at: datetime = Field(default=datetime.utcnow())
    status: int = Field(default=1, gt=0, lt=100)


class Product(BaseProduct, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class DBProduct(Product):
    pass


class CreateProduct(BaseProduct):
    pass


class PublicProduct(BaseProduct):
    id: int


class UpdateProduct(SQLModel):
    __tablename__ = "products"  # type: ignore
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    image_name: Optional[str] = None
    status: Optional[int] = None
