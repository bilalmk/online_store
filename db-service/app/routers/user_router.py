from shared.models.user import PublicUser
from app.config import sessionDep
from app.crud.user_crud import User_Crud
from fastapi import Depends, HTTPException, APIRouter
from shared.models.user import LoginRequest

router = APIRouter()
import sys


def get_user_crud(session: sessionDep) -> User_Crud:
    return User_Crud(session)


@router.post("/login", response_model=PublicUser)
async def login(login_request: LoginRequest, user_crud=Depends(get_user_crud)):
    try:
        username = login_request.username
        password = login_request.password
        user = user_crud.get_user(username)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user_crud.varify_password(password, user.password):
            raise HTTPException(status_code=200, detail="Invalid password")

        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
