import asyncio
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from fastapi import Depends, FastAPI
from app import config
from shared.models.user import User, CreateUser

#from app.kafka_consumer import consume_events
from app.kafka_producer import get_kafka_producer,AIOKafkaConsumer
from app.kafka_consumer import consume_events, get_kafka_consumer
from aiokafka import AIOKafkaProducer
import json

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("starting lifespan process")
    #await asyncio.sleep(10)
    #task = asyncio.create_task(consume_events(config.KAFKA_USER_DB_RESPONSE))
    yield

app = FastAPI(lifespan=lifespan, title="Hello World API with DB")

@app.get("/")
def main():
    return {"message": "Hello World from users"}


@app.post("/users/create")
async def create(user:CreateUser, producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)], consumer: Annotated[AIOKafkaConsumer, Depends(get_kafka_consumer)]):
    message = {
            "request_id": user.guid,
            "operation": "create",
            "entity": "user",
            "data": user.dict()
        }
    #print(type(user))
    obj = json.dumps(message).encode('utf-8')
    await producer.send(config.KAFKA_USER_TOPIC, value=obj)
    return {"message": "User registered successfully"}