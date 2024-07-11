import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import Depends, FastAPI, HTTPException
from app import config
from alembic.config import Config
# from app.kafka_consumer import consume_events
# from app.kafka_producer import get_kafka_producer
from app.kafka_consumer import consume_events
from alembic import command
import concurrent.futures
from app.routers import user_router,product_router


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
app.include_router(user_router.router)
app.include_router(product_router.router)


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/dbup")
async def dbup():
    await run_alembic_upgrade()
    return {"status": "ok"}

# @app.get("/")
# def main():
#     return {"message": "Hello World from db-service"}
