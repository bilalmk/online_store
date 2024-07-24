from app import config
from fastapi import Depends, HTTPException, status
import aiohttp
from shared.models.token import TokenData
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

oauth2_authentication = OAuth2PasswordBearer(tokenUrl="token")


async def get_token_data(token: str):
    """
    This function sends a POST request to an get_token_data endpoint of authentication microservice
    to retrieve user-date inside the token.
    """
    payload = aiohttp.FormData()
    payload.add_field("token", token)
    async with config.client_session.post(  # type: ignore
        f"{config.AUTH_API_BASE_PATH}/get_token_data", data=payload
    ) as response:
        if response.status != 200:
            res = await response.json()
            raise HTTPException(status_code=response.status, detail=res["detail"])
        data = await response.json()
        return data


async def get_token(token: Annotated[str, Depends(oauth2_authentication)]):
    """
    This function is used to validate the token and ensure that the user is authenticated.
    It calls the `get_token_data` function to fetch the token data from the authentication microservice.
    If the token data is valid and the user type is "user" not customer, it returns the validated `token_data`.
    Otherwise, it raises an HTTPException with a status code of 401 and a detail message indicating the issue.
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

    if token_data is None:
        raise credentials_exception

    return token_data


async def get_category_list():
    """
    This function asynchronously retrieves a list of category from a db-service microservice
    """
    db_service_url = f"{config.DB_API_BASE_PATH}/categories/"
    async with config.client_session.get(db_service_url) as response:
        data = await response.json()
        if response.status != 200:
            raise HTTPException(status_code=response.status, detail=data["detail"])
        return data


async def get_category(category_id: int):
    """
    This function sends a POST request to a database micro service to retrieve category information
    based on a given category ID.
    """
    payload = aiohttp.FormData()
    payload.add_field("category_id", category_id)
    db_service_url = f"{config.DB_API_BASE_PATH}/categories/category"
    async with config.client_session.post(db_service_url, data=payload) as response:
        if response.status != 200:
            res = await response.json()
            raise HTTPException(status_code=response.status, detail=res["detail"])
        data = await response.json()
        return data
