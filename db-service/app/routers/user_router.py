from shared.models.user import PublicUser
from app.config import sessionDep
from app.crud.user_crud import User_Crud
from fastapi import Depends, HTTPException, APIRouter, Form
from shared.models.user import LoginRequest
import sys


def get_user_crud(session: sessionDep) -> User_Crud:
    return User_Crud(session)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/login", response_model=PublicUser)
async def login(login_request: LoginRequest, user_crud=Depends(get_user_crud)):
    username = login_request.username
    password = login_request.password
    user = user_crud.get_user(username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_crud.varify_password(password, user.password)
    
    if not user_crud.varify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    return user

@router.post("/user", response_model=PublicUser)
async def get_user(userid: int = Form(...), user_crud=Depends(get_user_crud)):
    user = user_crud.get_user_by_id(userid)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.get("/", response_model=list[PublicUser])
async def get_users(user_crud=Depends(get_user_crud)):
    users = user_crud.get_users()
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return users