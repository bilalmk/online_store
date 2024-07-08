import asyncio
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator

from aiohttp import ClientSession, TCPConnector
from aiokafka import AIOKafkaProducer  # type: ignore
from fastapi import APIRouter, FastAPI, Depends
from app.kafka_consumer import consume_events
from app.kafka_producer import get_kafka_producer
from app import config
from app.operations import get_token

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("starting lifespan process")
    config.client_session = ClientSession(connector=TCPConnector(limit=100))
    yield
    await config.client_session.close()

app = FastAPI(lifespan=lifespan, title="Hello World API with DB")

router = APIRouter(
    prefix="/products",
    tags=["products"],
    dependencies=[Depends(get_token)],
    responses={404: {"description": "Not found"}},
)

@app.get("/")
def main():
    return {"message": "Hello World from products"}


@router.post("/create")
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
