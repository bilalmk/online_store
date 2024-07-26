from contextlib import asynccontextmanager
import sys
from typing import Annotated, AsyncGenerator
from fastapi import Depends, FastAPI, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app import config
from shared.models.customer import Customer, CreateCustomer, PublicCustomer, UpdateCustomer
from app.operations import (
    get_current_active_customer,
    authenticate_customer,
    create_token,
    get_customer_list,
)

from app.kafka_producer import get_kafka_producer
from app.kafka_consumer import (
    # consume_events,
    get_kafka_consumer,
    consume_response_from_kafka,
)
from aiokafka import AIOKafkaProducer
import json
from aiohttp import ClientSession, TCPConnector

oauth2_authentication = OAuth2PasswordBearer(tokenUrl="token")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("starting lifespan process")
    """
    # The line `config.client_session = ClientSession(connector=TCPConnector(limit=100))` is creating
    # an instance of `ClientSession` with a `TCPConnector` that has a limit of 100 connections. This
    # is used to manage connections to external services. The `limit=100` parameter sets the maximum number of simultaneous
    # connections that can be made using this `ClientSession`. This helps in controlling the number of
    # connections and managing resources efficiently when interacting with external services.
    """
    config.client_session = ClientSession(connector=TCPConnector(limit=100))
    yield
    await config.client_session.close()


app = FastAPI(lifespan=lifespan, title="Hello World API with DB")

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
    dependencies=[Depends(get_current_active_customer)],
    responses={404: {"description": "Not found"}},
)


# =======================default routes==========================
@app.get("/customer")
async def root():
    return {"message": "Hello World"}

@app.post("/customer/authentication")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    
    """this function is calling from operations file. this is authenticating the customer by calling customer login end-point from db-service"""
    customer: PublicCustomer = await authenticate_customer(form_data.username, form_data.password)
    customer = PublicCustomer.model_validate(customer)
    
    """calling authentication microservice to generate the token for existing customer"""
    token = await create_token(customer)
    return token


"""
- Endpoint to create a new customer in the system
- produce data to kafka topic, this topic is consumed by db-service
- db-service will produce response to kafka topic, kafka topic then consumed back by this api
- consumed response will be sent back to the customer
"""
@app.post("/customer/create")
async def create(
    customer: CreateCustomer, producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
):
    message = {
        "request_id": customer.guid,
        "operation": "create",
        "entity": "customer",
        "data": customer.dict(),
    }

    obj = json.dumps(message).encode("utf-8")
    await producer.send(config.KAFKA_CUSTOMER_TOPIC, value=obj)

    consumer = await get_kafka_consumer()
    try:
        """
        get response back of customer-create end point of db-service, 
        responsible to get topic data, perform db operation and sent status back to then caller endpoint
        """
        status_message = await consume_response_from_kafka(consumer, customer.guid)
    finally:
        await consumer.stop()

    if status_message:
        return status_message

    status_message = {"message": "Created"}
    return status_message


# =================================== Protected Routes =======================================
@router.get("/health")
async def call_db_service():
    db_service_url = f"{config.DB_API_BASE_PATH}/health"
    async with config.client_session.get(db_service_url) as response:
        return await response.json()


"""
- this endpoint is protected and can only be accessed by authenticated customers
- Endpoint to get the current login customer
- this endpoint calls db-service to get the login customer data
"""
@router.get("/me", response_model=PublicCustomer)
async def read_customers_me(
    current_customer: Annotated[Customer, Depends(get_current_active_customer)]
):
    return current_customer


"""
- this endpoint is protected and can only be accessed by authenticated customers
- Endpoint is enabled the logged-in customer to update his data
- this endpoint produce the data to kafka topic, kafka topic then consumed by db-service
- db-service will produce response to kafka topic, kafka topic then consumed back by this api
- consumed response will be sent back to the customer
"""
@router.patch("/update/{customer_guid_id}")
async def update_customer(
    customer: UpdateCustomer,
    customer_guid_id: str,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    current_customer: Annotated[Customer, Depends(get_current_active_customer)],
):
    customer_data = customer.model_dump(exclude_unset=True)
    
    if customer_data.get("password") and customer_guid_id != current_customer.guid:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="You can not change password of others",
        )
        
    if customer_data.get("status") and customer_guid_id == current_customer.guid:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="You can not change your own status",
        )

    message = {
        "request_id": customer_guid_id,
        "operation": "update",
        "entity": "customer",
        "data": customer_data,
    }

    obj = json.dumps(message).encode("utf-8")
    await producer.send(config.KAFKA_CUSTOMER_TOPIC, value=obj)

    consumer = await get_kafka_consumer()
    try:
        """
        get response back from db-service, 
        db-service is responsible to collect topic data 
        perform db operation and produce response data to kafka topic        
        """
        status_message = await consume_response_from_kafka(consumer, customer_guid_id)
    finally:
        await consumer.stop()

    if status_message:
        return status_message

    status_message = {"message": "Try again"}
    return status_message

app.include_router(router)
