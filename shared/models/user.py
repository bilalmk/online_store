from typing import Optional
import uuid
from sqlmodel import SQLModel, Field


class BaseUser(SQLModel):
    __tablename__ = "users"  # type: ignore
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=3, max_length=255)
    first_name: Optional[str] = Field(min_length=0, max_length=255)
    last_name: Optional[str] = Field(min_length=0, max_length=255)
    address: Optional[str] = None
    phone_number: Optional[str] = Field(min_length=0, max_length=20)
    guid: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), max_length=40
    )


class User(BaseUser, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str
    
class DBUser(User):
    pass

class LoginRequest(SQLModel):
    username: str
    password: str

class CreateUser(BaseUser):
    password: str


class PublicUser(BaseUser):
    id: int


class UpdateUser(SQLModel):
    __tablename__ = "users"  # type: ignore
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
