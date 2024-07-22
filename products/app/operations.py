import sys
from app import config
import json
from fastapi import Depends, HTTPException, status
import aiohttp
from shared.models.inventory import InventoryProductUpdate
from shared.models.token import TokenData
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

oauth2_authentication = OAuth2PasswordBearer(tokenUrl="token")


async def get_token_data(token: str):
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
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data: TokenData = await get_token_data(token)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    token_data = TokenData.model_validate(token_data)

    if token_data is None:
        raise credentials_exception

    return token_data


async def get_product_list():
    db_service_url = f"{config.DB_API_BASE_PATH}/products/"
    async with config.client_session.get(db_service_url) as response:
        data = await response.json()
        if response.status != 200:
            raise HTTPException(status_code=response.status, detail=data["detail"])
        return data


async def get_product(product_id: int):
    payload = aiohttp.FormData()
    payload.add_field("product_id", product_id)
    db_service_url = f"{config.DB_API_BASE_PATH}/products/product"
    async with config.client_session.post(db_service_url, data=payload) as response:
        if response.status != 200:
            res = await response.json()
            raise HTTPException(status_code=response.status, detail=res["detail"])
        data = await response.json()
        return data


async def get_categories(category_id: int):
    payload = aiohttp.FormData()
    payload.add_field("category_id", category_id)
    db_service_url = f"{config.DB_API_BASE_PATH}/categories/category"
    async with config.client_session.post(db_service_url, data=payload) as response:
        if response.status != 200:
            return None
        data = await response.json()
        return data


async def get_category_list():
    db_service_url = f"{config.DB_API_BASE_PATH}/categories/"
    async with config.client_session.get(db_service_url) as response:
        data = await response.json()
        if response.status != 200:
            return None
        return data


async def get_brands(brand_id: int):
    payload = aiohttp.FormData()
    payload.add_field("brand_id", brand_id)
    db_service_url = f"{config.DB_API_BASE_PATH}/brands/brand"
    async with config.client_session.post(db_service_url, data=payload) as response:
        if response.status != 200:
            return None
        data = await response.json()
        return data


async def get_brand_list():
    db_service_url = f"{config.DB_API_BASE_PATH}/brands/"
    async with config.client_session.get(db_service_url) as response:
        data = await response.json()
        if response.status != 200:
            return None
        return data


async def update_product_inventory(inventory_data: list[InventoryProductUpdate]):
    # print("update_product_inventory1")
    # print(inventory_data.get("inventory_info"))
    # sys.stdout.flush()
    db_service_url = f"{config.DB_API_BASE_PATH}/products/inventory"
    async with config.client_session.put(db_service_url, json=inventory_data.get("inventory_info")) as response:
        # print("response")
        # print(response)
        # sys.stdout.flush()
        if response.status != 200:
            return None
        data = await response.json()
        # print("update_product_inventory_response")
        # print(data)
        # sys.stdout.flush()
        return data
