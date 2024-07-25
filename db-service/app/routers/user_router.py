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

"""
End-Point handles user login by verifying the username and password provided in the
request

user_crud is a dependency that is used to interact with user data in the database. it contains methods for retrieving user information
and verifying passwords
"""
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

"""
- End-Point retrieves a user by their ID and returns a PublicUser model, raising a 404 error if the user is not found
- user_crud is a dependency that is used to interact with user data in the database. it contains methods for retrieving user information
"""
@router.post("/user", response_model=PublicUser)
async def get_user(userid: int = Form(...), user_crud=Depends(get_user_crud)):
    user = user_crud.get_user_by_id(userid)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

"""
- End-Point retrieves a list of users and returns them as a response, raising a 404 error if no users are found
- user_crud class is a dependency that is used to interact with user data in the database. it contains methods for retrieving user information
"""
@router.get("/", response_model=list[PublicUser])
async def get_users(user_crud=Depends(get_user_crud)):
    users = user_crud.get_users()
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return users
