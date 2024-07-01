import asyncio
from contextlib import asynccontextmanager
import sys
from typing import Annotated, AsyncGenerator
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app import config
from shared.models.user import User, CreateUser

# from app.kafka_consumer import consume_events
from app.kafka_producer import get_kafka_producer
from app.kafka_consumer import (
    # consume_events,
    get_kafka_consumer,
    consume_response_from_kafka,
    responses,
)
from aiokafka import AIOKafkaProducer
import json
import aiohttp


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
    try:
        payload = {"username": username, "password": password}
        async with app.state.aiohttp_session.post(
            str(config.DB_API_BASE_PATH) + "/login", data=json.dumps(payload)
        ) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=response.status, detail="Failed to send data"
                )
            data = await response.json()
            return {"response": data}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def main():
    return {"message": "Hello World from users"}


@app.post("/user/authentication")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        user = authenticate_user(form_data.username, form_data.password)
    except Exception as e:
        raise HTTPException(
            status_code=200,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


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
