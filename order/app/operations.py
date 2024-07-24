from app import config
import json
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

    if not token_data or token_data.get("user_type") != "customer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    token_data = TokenData.model_validate(token_data)

    if token_data is None:
        raise credentials_exception

    return token_data


async def get_order(order_id: str):
    """
    This function sends a POST request to a order micro service to retrieve order information
    based on a given order ID.
    """
    payload = aiohttp.FormData()
    payload.add_field("order_id", order_id)
    db_service_url = f"{config.DB_API_BASE_PATH}/orders/order"
    async with config.client_session.post(db_service_url, data=payload) as response:
        if response.status != 200:
            res = await response.json()
            raise HTTPException(status_code=response.status, detail=res["detail"])
        data = await response.json()
        return data


async def get_order_products(product_ids: str):
    """
    This function sends a POST request to a product micro service to retrieve list of products 
    based on a given product ids.
    """
    payload = aiohttp.FormData()
    payload.add_field("product_ids", product_ids)
    db_service_url = f"{config.DB_API_BASE_PATH}/products/product_by_ids"
    async with config.client_session.post(db_service_url, data=payload) as response:
        if response.status != 200:
            return None
        data = await response.json()
        return data
