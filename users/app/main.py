from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from fastapi import Depends, FastAPI, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app import config
from shared.models.user import User, CreateUser, PublicUser, UpdateUser
from app.operations import (
    get_current_active_user,
    authenticate_user,
    create_token,
    get_user_list,
)

from app.kafka_producer import get_kafka_producer
from app.kafka_consumer import (
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
    # The line `config.client_session = ClientSession(connector=TCPConnector(limit=100))` is creating
    # an instance of `ClientSession` with a `TCPConnector` that has a limit of 100 connections. This
    # is used to manage connections to external services. The `limit=100` parameter sets the maximum number of simultaneous
    # connections that can be made using this `ClientSession`. This helps in controlling the number of
    # connections and managing resources efficiently when interacting with external services.
    config.client_session = ClientSession(connector=TCPConnector(limit=100))
    yield
    await config.client_session.close()


app = FastAPI(lifespan=lifespan, title="Hello World API with DB")

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)


# =======================default routes==========================
@app.get("/user")
async def root():
    return {"message": "Hello World"}

@app.post("/user/authentication")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    
    """this function is calling from operations file. this is authenticating the user calling user login end-point from db-service"""
    user: PublicUser = await authenticate_user(form_data.username, form_data.password)
    user = PublicUser.model_validate(user)

    """calling authentication microservice to generate the token for existing user"""
    token = await create_token(user)
    return token


"""
- Endpoint to create a new user in the system
- produce data to kafka topic, this topic is consumed by db-service
- db-service will produce response to kafka topic, this topic is consumed back by this api
- consumed response will be sent back to the user
"""
@app.post("/users/create")
async def create(
    user: CreateUser, producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
):
    message = {
        "request_id": user.guid,
        "operation": "create",
        "entity": "user",
        "data": user.dict(),
    }

    obj = json.dumps(message).encode("utf-8")
    await producer.send(config.KAFKA_USER_TOPIC, value=obj)

    consumer = await get_kafka_consumer()
    try:
        """
            get response back of usercreate end point of db-service, 
            responsible to get topic data perform db operation and sent status back to parent endpoint
        """
        status_message = await consume_response_from_kafka(consumer, user.guid)
    finally:
        await consumer.stop()   

    if status_message:
        return status_message

    status_message = {"message": "Created"}
    return status_message


# =================================== Protected Routes =======================================
"""
- Endpoint to get the list of all users in the system
- this endpoint is protected and can only be accessed by authenticated users
- this endpoint calls db-service to get the list of users
"""
@router.get("/", response_model=list[PublicUser])
async def get_users():
    list = await get_user_list()
    return list


@router.get("/health")
async def call_db_service():
    db_service_url = f"{config.DB_API_BASE_PATH}/health"
    async with config.client_session.get(db_service_url) as response:
        return await response.json()


"""
- Endpoint to get the current login user
- this endpoint is protected and can only be accessed by authenticated users
- this endpoint calls db-service to get the login user data
"""
@router.get("/me", response_model=PublicUser)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


"""
- Endpoint to is enabled the logged-in user to update his data
- this endpoint is protected and can only be accessed by authenticated users
- this endpoint produce the data to kafka topic, this topic is consumed by db-service
- db-service will produce response to kafka topic, this topic is consumed back by this api
- consumed response will be sent back to the user
"""
@router.patch("/update/{user_guid_id}")
async def update_user(
    user: UpdateUser,
    user_guid_id: str,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    user_data = user.model_dump(exclude_unset=True)
    
    if user_data.get("password") and user_guid_id != current_user.guid:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="You can not change password of others",
        )
        
    if user_data.get("status") and user_guid_id == current_user.guid:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="You can not change your own status",
        )

    message = {
        "request_id": user_guid_id,
        "operation": "update",
        "entity": "user",
        "data": user_data,
    }

    obj = json.dumps(message).encode("utf-8")
    await producer.send(config.KAFKA_USER_TOPIC, value=obj)

    consumer = await get_kafka_consumer()
    try:
        """
        get response back from db-service, 
        db-service is responsible to collect topic data 
        perform db operation and produce response data to kafka topic        
        """
        status_message = await consume_response_from_kafka(consumer, user_guid_id)
    finally:
        await consumer.stop()

    if status_message:
        return status_message

    status_message = {"message": "Try again"}
    return status_message


"""
- Endpoint to is use to soft delete the user from db
- this endpoint is protected and can only be accessed by authenticated users
- this endpoint produce the data to kafka topic, this topic is consumed by db-service
- db-service will produce response to kafka topic, this topic is consumed back by this api
- consumed response will be sent back to the user
"""
@router.delete("/delete/{user_guid_id}")
async def delete_user(
    user_guid_id: str,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    try:
        if user_guid_id == current_user.guid:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="You can not delete yourself",
            )

        message = {
            "request_id": user_guid_id,
            "operation": "delete",
            "entity": "user",
            "data": {},
        }

        obj = json.dumps(message).encode("utf-8")
        await producer.send(config.KAFKA_USER_TOPIC, value=obj)

        consumer = await get_kafka_consumer()
        try:
            status_message = await consume_response_from_kafka(consumer, user_guid_id)
        finally:
            await consumer.stop()

        if status_message:
            return status_message

        status_message = {"message": "Try again"}
        return status_message

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(router)
