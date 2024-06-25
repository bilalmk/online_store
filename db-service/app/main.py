import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from app import config
from shared.models.user import User

#from app.kafka_consumer import consume_events
#from app.kafka_producer import get_kafka_producer
from app.kafka_consumer import consume_events

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("starting lifespan process")
    await asyncio.sleep(10)
    asyncio.create_task(consume_events(config.KAFKA_USER_TOPIC, config.KAFKA_USER_CONSUMER_GROUP_ID))
    asyncio.create_task(consume_events(config.KAFKA_PRODUCT_TOPIC,config.KAFKA_PRODUCT_CONSUMER_GROUP_ID))
    yield

app = FastAPI(lifespan=lifespan, title="Hello World db service API")

@app.get("/")
def main():
    return {"message": "Hello World from db-service"}