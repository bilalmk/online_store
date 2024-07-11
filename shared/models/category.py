from datetime import datetime
from decimal import Decimal
import re
from typing import Optional
import uuid
from fastapi import File
from pydantic import Extra, validator, root_validator
from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy import DECIMAL, Float


class BaseCategory(SQLModel):
    __tablename__ = "categories"  # type: ignore
    parent_id: Optional[int] = Field(default=0)
    category_name: str = Field(..., min_length=3, max_length=255)
    category_slug: Optional[str] = Field(default=None, max_length=255)
    guid: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), max_length=40
    )
    created_by: Optional[int] = Field(..., gt=0)
    created_at: datetime = Field(default=datetime.utcnow())
    status: int = Field(default=1, gt=0, lt=100)
    

class Category(BaseCategory, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class DBCategory(Category):
    pass


class CreateCategory(BaseCategory):
    @validator("category_slug", pre=True, always=True)
    def generate_slug(cls, v, values):
        if 'category_name' in values:
            return cls.slugify(values['category_name'])
        return v

    @staticmethod
    def slugify(value: str) -> str:
        value = value.lower()
        value = re.sub(r'\s+', '-', value)  # Replace spaces with hyphens
        value = re.sub(r'[^\w-]', '', value)  # Remove all non-word characters
        return value

    class Config:
        extra = Extra.forbid

class PublicCategory(BaseCategory):
    id: int


class UpdateCategory(SQLModel):
    __tablename__ = "categories"  # type: ignore
    parent_id: Optional[int] = Field(default=None)
    category_name: Optional[str] = Field(default=None)
    category_slug: Optional[str] = Field(default=None)
    status: Optional[int] = Field(default=None)
    
    #@validator("category_slug", pre=True, always=True)
    @root_validator(pre=True)
    def generate_slug(cls, values):
        if 'category_name' in values and 'category_slug' not in values:
            values['category_slug'] = cls.slugify(values['category_name'])
        return values

    @staticmethod
    def slugify(value: str) -> str:
        value = value.lower()
        value = re.sub(r'\s+', '-', value)  # Replace spaces with hyphens
        value = re.sub(r'[^\w-]', '', value)  # Remove all non-word characters
        return value

    class Config:
        extra = Extra.forbid
