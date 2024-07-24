from app import config
import json
from fastapi import Depends, HTTPException, status
import aiohttp
from shared.models.customer import Customer, PublicCustomer
from shared.models.token import CustomerTokenData
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, AsyncGenerator

oauth2_authentication = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_customer(username: str, password: str):
    """
    This function sends a POST request to a customer authentication endpoint to the db-service micorservice 
    with provided username and password, handling response status codes accordingly.
    """
    payload = {"username": username, "password": password}
    headers = {"Content-Type": "application/json"}
    async with config.client_session.post(
        f"{config.DB_API_BASE_PATH}/customers/login",
        data=json.dumps(payload),
        headers=headers,
    ) as response:
        if response.status != 200:
            res = await response.json()
            print(res)
            raise HTTPException(status_code=response.status, detail=res["detail"])
        data = await response.json()
        return data


async def get_customer(customer_id: int):
    """
    This function sends a POST request to a db-service microservice to retrieve customer data based on the
    provided customer ID.
    """
    payload = aiohttp.FormData()
    payload.add_field("customer_id", customer_id)

    async with config.client_session.post(
        f"{config.DB_API_BASE_PATH}/customers/customer",
        data=payload,
    ) as response:
        if response.status != 200:
            res = await response.json()
            raise HTTPException(status_code=response.status, detail=res["detail"])
        data = await response.json()
        return data
    
async def get_customer_list():
    """
    This function sends a GET request to a db-service microservice to retrieve list of customers.    
    """
    db_service_url = f"{config.DB_API_BASE_PATH}/customers/"
    async with config.client_session.get(db_service_url) as response:
        data = await response.json()
        print(data)
        print(response.status)
        if response.status != 200:
            raise HTTPException(status_code=response.status, detail=data["detail"])
        return data


async def create_token(customer: PublicCustomer):
    """
    This function creates a token for a customer by sending a POST request to an generate_token
    endpoint of authentication microservice.
    """
    payload = aiohttp.FormData()
    payload.add_field("username", customer.username)
    payload.add_field("id", customer.id)
    payload.add_field("guid", customer.guid)
    payload.add_field("user_type", "customer")

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
    to retrieve customer-date inside the token.
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
    
async def get_current_customer(token: Annotated[str, Depends(oauth2_authentication)]):
    """
    This function retrieves the current customer based on the provided token after
    validating the credentials.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data: CustomerTokenData = await get_token_data(token)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    token_data = CustomerTokenData.model_validate(token_data)
    
    customer = await get_customer(token_data.customer_id)
    
    if customer is None:
        raise credentials_exception

    return PublicCustomer.model_validate(customer)


def get_current_active_customer(current_customer: Annotated[Customer, Depends(get_current_customer)]):
    """
    This function retrieves the current active customer and raises an exception 
    if the customer status is 0 or inActive.   
    """
    if current_customer.status == 0:
        raise HTTPException(status_code=400, detail="Inactive customer")
    return current_customer