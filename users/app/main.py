from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app import config
from shared.models.user import User, CreateUser, PublicUser
from shared.models.token import TokenData

# from app.kafka_consumer import consume_events
from app.kafka_producer import get_kafka_producer
from app.kafka_consumer import (
    # consume_events,
    get_kafka_consumer,
    consume_response_from_kafka,
)
from aiokafka import AIOKafkaProducer
import json
import aiohttp

oauth2_authentication = OAuth2PasswordBearer(tokenUrl="token")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("starting lifespan process")
    # await asyncio.sleep(10)
    # task = asyncio.create_task(consume_events(config.KAFKA_USER_DB_RESPONSE))

    app.state.aiohttp_session = aiohttp.ClientSession()
    yield
    await app.state.aiohttp_session.close()


app = FastAPI(lifespan=lifespan, title="Hello World API with DB")


async def authenticate_user(username: str, password: str):
    payload = {"username": username, "password": password}
    headers = {"Content-Type": "application/json"}
    async with app.state.aiohttp_session.post(
        f"{config.DB_API_BASE_PATH}/login",
        data=json.dumps(payload),
        headers=headers,
    ) as response:
        if response.status != 200:
            res = await response.json()
            print(res)
            raise HTTPException(status_code=response.status, detail=res["detail"])
        data = await response.json()
        return data


async def get_user(userid: int):
    payload = aiohttp.FormData()
    payload.add_field("userid", userid)

    async with app.state.aiohttp_session.post(
        f"{config.DB_API_BASE_PATH}/user",
        data=payload,
    ) as response:
        if response.status != 200:
            res = await response.json()
            raise HTTPException(status_code=response.status, detail=res["detail"])
        data = await response.json()
        return data


async def create_token(user: PublicUser):
    payload = aiohttp.FormData()
    payload.add_field("username", user.username)
    payload.add_field("id", user.id)

    async with app.state.aiohttp_session.post(
        f"{config.AUTH_API_BASE_PATH}/generate_token", data=payload
    ) as response:
        if response.status != 200:
            res = await response.json()
            raise HTTPException(status_code=response.status, detail=res["detail"])
        data = await response.json()
        return data


async def get_token_data(token: str):
    payload = aiohttp.FormData()
    payload.add_field("token", token)
    async with app.state.aiohttp_session.post(
        f"{config.AUTH_API_BASE_PATH}/get_token_data", data=payload
    ) as response:
        if response.status != 200:
            res = await response.json()
            raise HTTPException(status_code=response.status, detail=res["detail"])
        data = await response.json()
        return data


@app.get("/")
def main():
    return {"message": "Hello World from users"}


@app.get("/user/health")
async def call_db_service():
    db_service_url = "http://db-service:8000/health"
    async with app.state.aiohttp_session.get(db_service_url) as response:
        return await response.json()


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


async def get_current_user(token: Annotated[str, Depends(oauth2_authentication)]):
    
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
    
    user = await get_user(token_data.userid)
    
    if user is None:
        raise credentials_exception
    
    return PublicUser.model_validate(user)


def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.status == 0:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.get("/users/me/", response_model=PublicUser)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user
