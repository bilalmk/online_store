from app import config
import json
from fastapi import Depends, HTTPException, status
import aiohttp
from shared.models.user import User, PublicUser
from shared.models.token import TokenData
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

oauth2_authentication = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_user(username: str, password: str):
    """
        This function sends a POST request to a user authentication endpoint to the db-service micorservice 
        with provided username and password, handling response status codes accordingly.
    """
    payload = {"username": username, "password": password}
    headers = {"Content-Type": "application/json"}
    async with config.client_session.post(
        f"{config.DB_API_BASE_PATH}/users/login",
        data=json.dumps(payload),
        headers=headers,
    ) as response:
        if response.status != 200:
            res = await response.json()
            raise HTTPException(status_code=response.status, detail=res["detail"])
        data = await response.json()
        return data


async def get_user(userid: int):
    """
        This function sends a POST request to a db-service microservice to retrieve user data based on the
        provided user ID.
    """
    payload = aiohttp.FormData()
    payload.add_field("userid", userid)

    async with config.client_session.post(
        f"{config.DB_API_BASE_PATH}/users/user",
        data=payload,
    ) as response:
        if response.status != 200:
            res = await response.json()
            raise HTTPException(status_code=response.status, detail=res["detail"])
        data = await response.json()
        return data
    
async def get_user_list():
    """
        This function sends a GET request to a db-service microservice to retrieve list of users.    
    """
    db_service_url = f"{config.DB_API_BASE_PATH}/users/"
    async with config.client_session.get(db_service_url) as response:
        data = await response.json()
        if response.status != 200:
            raise HTTPException(status_code=response.status, detail=data["detail"])
        return data


async def create_token(user: PublicUser):
    """
        This function creates a token for a user by sending a POST request to an generate_token
        endpoint of authentication microservice.
    """
    payload = aiohttp.FormData()
    payload.add_field("username", user.username)
    payload.add_field("id", user.id)
    payload.add_field("guid", user.guid)
    payload.add_field("user_type", "user")
    
    async with config.client_session.post(
        f"{config.AUTH_API_BASE_PATH}/generate_token", data=payload
    ) as response:
        if response.status != 200:
            res = await response.json()
            raise HTTPException(status_code=response.status, detail=res["detail"])
        data = await response.json()
        return data


async def get_token_data(token: str):
    """
    This function sends a POST request to an get_token_data endpoint of authentication microservice
    to retrieve user-date inside the token.
    """
    payload = aiohttp.FormData()
    payload.add_field("token", token)
    async with config.client_session.post(
        f"{config.AUTH_API_BASE_PATH}/get_token_data", data=payload
    ) as response:
        if response.status != 200:
            res = await response.json()
            raise HTTPException(status_code=response.status, detail=res["detail"])
        data = await response.json()
        return data
    
async def get_current_user(token: Annotated[str, Depends(oauth2_authentication)]):
    """
        This function retrieves the current user based on the provided token after
        validating the credentials.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data: TokenData = await get_token_data(token)

    if not token_data or token_data.get("user_type") != "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    token_data = TokenData.model_validate(token_data)
    
    user = await get_user(token_data.userid)
    
    if user is None:
        raise credentials_exception

    return PublicUser.model_validate(user)


def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    """
        This function retrieves the current active user and raises an exception if the user status is 0 or inactive.   
    """
    if current_user.status == 0:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user