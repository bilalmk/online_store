import json
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from aiohttp import ClientSession, TCPConnector
from fastapi import APIRouter, FastAPI, Depends
from aiokafka import AIOKafkaProducer  # type: ignore
from app.kafka_producer import get_kafka_producer
from app.kafka_consumer import (
    get_kafka_consumer,
    consume_response_from_kafka,
)

from app import config
from app.operations import get_token
from shared.models.product import CreateProduct
from shared.models.token import Token, TokenData

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
    product: CreateProduct, producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    token: Annotated[TokenData, Depends(get_token)]
):
    product.created_by = token.userid
    message = {
        "request_id": product.guid,
        "operation": "create",
        "entity": "product",
        "data": product.dict(),
    }
    try:
        # print(type(user))
        obj = json.dumps(message).encode("utf-8")
        print(obj)
        # await producer.send(config.KAFKA_PRODUCT_TOPIC, value=obj)
        # await asyncio.sleep(10)
    except Exception as e:
        return str(e)

    # raise HTTPException(status_code=500, detail="No response from db-service")
    # consumer = await get_kafka_consumer()
    # try:
    #     status_message = await consume_response_from_kafka(consumer, product.guid)
    # finally:
    #     await consumer.stop()

    # if status_message:
    #     return status_message

    status_message = {"message": "Created"}
    return status_message

app.include_router(router)