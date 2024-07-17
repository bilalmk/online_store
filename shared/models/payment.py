from typing import Optional
from pydantic import BaseModel
from sqlalchemy import false
class PaymentInfo(BaseModel):
    card_number: str
    expiration_date: str  # Format: "YYYY-MM"
    card_code: str
    amount: float
    order_id:str
    
class PaymentSuccessStatus(BaseModel):
    transaction_id:Optional[str] = None
    response_code:Optional[int] = None
    message_code:Optional[int] = None
    message:Optional[str] = None
    
class PaymentFailure(BaseModel):
    error_code:Optional[int] = None
    error_message:Optional[str] = None
    message:Optional[str] = None
    is_error:Optional[bool]=False
    