from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel
from sqlalchemy import false
from sqlmodel import Field, SQLModel

class BasePayment(SQLModel):
    __tablename__ = "payments"  # type: ignore
    order_id: int = Field(...)
    customer_id: int = Field(...)
    transaction_id: str = Field(...)
    payment_gateway: str = Field(...)
    amount: float = Field(...)
    payment_date: Optional[datetime] = Field(default=datetime.utcnow())
    status: int = Field(default=1)

class Payment(BasePayment, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
class CreatePayment(BasePayment):
    pass

class PublicPayment(BasePayment):
    id: int
    
class PaymentInfo(BaseModel):
    card_number: str
    expiration_date: str  # Format: "YYYY-MM"
    card_code: str
    amount: float
    order_id: int
    customer_id: int


class PaymentSuccessStatus(BaseModel):
    transaction_id: Optional[str] = None
    response_code: Optional[int] = None
    message_code: Optional[int] = None
    message: Optional[str] = None


class PaymentFailure(BaseModel):
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    message: Optional[str] = None
    is_error: Optional[bool] = False
    
class PaymentStatus(BaseModel):
    status: Optional[bool] = None
    message: Optional[Union[PaymentSuccessStatus, PaymentFailure]] = None
