from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid
from sqlmodel import SQLModel, Field


class BaseProduct(SQLModel):
    __tablename__ = "products"  # type: ignore
    name: str = Field(sa_column_kwargs={"nullable": False, "length": 255})
    description: Optional[str] = None
    price: Decimal = Field(
        sa_column_kwargs={"nullable": False, "scale": 2, "precision": 10}
    )
    stock_quantity: int = Field(sa_column_kwargs={"nullable": False})
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    brand_id: Optional[int] = Field(default=None, foreign_key="brands.id")
    image_name: Optional[str] = Field(default=None, sa_column_kwargs={"length": 255})
    guid: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), max_length=40
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP"},
    )
    status: Optional[int] = Field(default=1, gt=0, lt=100)


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
