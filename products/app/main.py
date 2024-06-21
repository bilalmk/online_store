import asyncio
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI, Depends
from app.kafka_consumer import consume_events
from app.kafka_producer import get_kafka_producer

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    task = asyncio.create_task(consume_events('order', 'broker:19092'))
    yield

@app.get("/")
def main():
    return {"message": "Hello World from products"}

@app.get("/products/create")
async def create(producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    await producer.send("order", b"Hello World")
    return {"message": "products"}

@app.get("/products") 
async def view_products():
    await consume_events('order', 'broker:19092')