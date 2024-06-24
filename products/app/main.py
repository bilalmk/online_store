import asyncio
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from aiokafka import AIOKafkaProducer  # type: ignore
from fastapi import FastAPI, Depends
from app.kafka_consumer import consume_events
from app.kafka_producer import get_kafka_producer
from app import config

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("starting lifespan process")
    await asyncio.sleep(10)
    task = asyncio.create_task(consume_events(config.KAFKA_ORDER_TOPIC, config.BOOTSTRAP_SERVER))
    yield

app = FastAPI(lifespan=lifespan, title="Hello World API with DB")

@app.get("/")
def main():
    return {"message": "Hello World from products"}


@app.get("/products/create")
async def create(producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    await producer.send(config.KAFKA_ORDER_TOPIC, b"Hello World from products")
    return {"message": "products"}
