import asyncio
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from fastapi import Depends, FastAPI
from app import config
from confluent_kafka import Producer
from shared.models.user import User

#from app.kafka_consumer import consume_events
from app.kafka_producer import get_kafka_producer
from app.kafka_consumer import consume_events

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("starting lifespan process")
    #await asyncio.sleep(10)
    #task = asyncio.create_task(consume_events(config.KAFKA_USER_TOPIC))
    yield

app = FastAPI(lifespan=lifespan, title="Hello World API with DB")

@app.get("/")
def main():
    return {"message": "Hello World from users"}


@app.get("/users/create")
async def create(user:User, producer: Annotated[Producer, Depends(get_kafka_producer)]):
    await producer.send(config.KAFKA_USER_TOPIC, user.encode('utf-8'))
    return {"message": "User registered successfully"}
