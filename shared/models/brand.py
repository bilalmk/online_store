from datetime import datetime
from decimal import Decimal
import re
from typing import Optional
import uuid
from fastapi import File
from pydantic import Extra, root_validator, validator
from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy import DECIMAL, Float


class BaseBrand(SQLModel):
    __tablename__ = "brands"  # type: ignore
    brand_name: str = Field(..., min_length=3, max_length=255)
    brand_slug: Optional[str] = Field(default=None, max_length=255)
    guid: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), max_length=40
    )
    created_by: int = Field(..., gt=0)
    created_at: datetime = Field(default=datetime.utcnow())
    status: int = Field(default=1, gt=0, lt=100)

class Brand(BaseBrand, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class DBBrand(Brand):
    pass


class CreateBrand(BaseBrand):
    @validator("brand_slug", pre=True, always=True)
    def generate_slug(cls, v, values):
        if 'brand_name' in values:
            return cls.slugify(values['brand_name'])
        return v

    @staticmethod
    def slugify(value: str) -> str:
        value = value.lower()
        value = re.sub(r'\s+', '-', value)  # Replace spaces with hyphens
        value = re.sub(r'[^\w-]', '', value)  # Remove all non-word characters
        return value

    class Config:
        extra = Extra.forbid


class PublicBrand(BaseBrand):
    id: int


class UpdateBrand(SQLModel):
    __tablename__ = "brands"  # type: ignore
    brand_name: Optional[str] = None
    brand_slug: Optional[str] = None
    status: Optional[int] = None
    
    @root_validator(pre=True)
    def generate_slug(cls, values):
        if 'brand_name' in values and 'brand_slug' not in values:
            values['brand_slug'] = cls.slugify(values['brand_name'])
        return values

    @staticmethod
    def slugify(value: str) -> str:
        value = value.lower()
        value = re.sub(r'\s+', '-', value)  # Replace spaces with hyphens
        value = re.sub(r'[^\w-]', '', value)  # Remove all non-word characters
        return value

    class Config:
        extra = Extra.forbid
