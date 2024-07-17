from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    user_name: str

class TokenData(BaseModel):
    username: Optional[str] = None
    userid: int