from contextlib import asynccontextmanager
import sys
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

# from app.kafka_consumer import consume_events
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
    # await asyncio.sleep(10)
    # task = asyncio.create_task(consume_events(config.KAFKA_USER_DB_RESPONSE))
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
    user: PublicUser = await authenticate_user(form_data.username, form_data.password)
    user = PublicUser.model_validate(user)
    token = await create_token(user)
    return token


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

    # print(type(user))
    obj = json.dumps(message).encode("utf-8")
    await producer.send(config.KAFKA_USER_TOPIC, value=obj)
    # await asyncio.sleep(10)

    # raise HTTPException(status_code=500, detail="No response from db-service")
    consumer = await get_kafka_consumer()
    try:
        status_message = await consume_response_from_kafka(consumer, user.guid)
    finally:
        await consumer.stop()

    if status_message:
        return status_message

    status_message = {"message": "Created"}
    return status_message


# =================================== Protected Routes =======================================
@router.get("/", response_model=list[PublicUser])
async def get_users():
    list = await get_user_list()
    return list


@router.get("/health")
async def call_db_service():
    db_service_url = f"{config.DB_API_BASE_PATH}/health"
    async with config.client_session.get(db_service_url) as response:
        return await response.json()


@router.get("/me", response_model=PublicUser)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


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
        status_message = await consume_response_from_kafka(consumer, user_guid_id)
    finally:
        await consumer.stop()

    if status_message:
        return status_message

    status_message = {"message": "Try again"}
    return status_message


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
