from typing import Optional
from sqlmodel import SQLModel, Field

class BaseUser(SQLModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=3, max_length=255)
    full_name: Optional[str] = Field(min_length=0, max_length=255)
    address: Optional[str] = None
    phone_number: Optional[str] = Field(min_length=0, max_length=20)
    
class User(BaseUser, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class CreateUser(BaseUser):
    password:str
class PublicUser(BaseUser):
    id:int
    password_hash: str
    
class UpdateUser(SQLModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None