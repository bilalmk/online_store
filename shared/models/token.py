from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    user_name: str
    user_type: Optional[str] = "user"

class TokenData(BaseModel):
    username: Optional[str] = None
    userid: int
    
class CustomerTokenData(BaseModel):
    username: Optional[str] = None
    customer_id: int