import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from app import config
from shared.models.user import User
from alembic.config import Config

# from app.kafka_consumer import consume_events
# from app.kafka_producer import get_kafka_producer
from app.kafka_consumer import consume_events
from alembic import command
import concurrent.futures

alembic_cfg = Config("alembic.ini")

async def run_alembic_upgrade():
    # Create a thread pool executor
    executor = concurrent.futures.ThreadPoolExecutor()

    # Schedule the Alembic upgrade to run in a separate thread
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, command.upgrade, alembic_cfg, "head")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("starting lifespan process")
    
    # executor = concurrent.futures.ThreadPoolExecutor()
    
    # loop = asyncio.get_event_loop()
    # await loop.run_in_executor(executor, command.upgrade, alembic_cfg, "head")
    
    await asyncio.sleep(10)
    asyncio.create_task(
        consume_events(config.KAFKA_USER_TOPIC, config.KAFKA_USER_CONSUMER_GROUP_ID)
    )
    asyncio.create_task(
        consume_events(
            config.KAFKA_PRODUCT_TOPIC, config.KAFKA_PRODUCT_CONSUMER_GROUP_ID
        )
    )
    asyncio.create_task(run_alembic_upgrade())
    # asyncio.create_task(
    #     command.upgrade(alembic_cfg, "head")
    # )
    yield


app = FastAPI(lifespan=lifespan, title="Hello World db service API")

# @app.on_event("startup")
# async def startup_event():
#     # Schedule Alembic upgrade to run in the background
#     asyncio.create_task(run_alembic_upgrade())


@app.get("/")
def main():
    return {"message": "Hello World from db-service"}
