import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import Depends, FastAPI, HTTPException
from app import config
from alembic.config import Config

from app.kafka_consumer import consume_events
from alembic import command
import concurrent.futures
from app.routers import (
    user_router,
    product_router,
    category_router,
    brand_router,
    order_router,
    payment_router,
    customer_router
)


alembic_cfg = Config("alembic.ini")


async def run_alembic_upgrade():
    """
    This function uses a thread pool executor to run the Alembic upgrade command in
    a separate thread.
    
    Microservice will execute this data-base migration script when it will be up for first time
    """
    # Create a thread pool executor
    executor = concurrent.futures.ThreadPoolExecutor()

    # Schedule the Alembic upgrade to run in a separate thread
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, command.upgrade, alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("starting lifespan process")
    
    """
    The `asyncio.create_task()` function is used to create a task to run a coroutine concurrently in
    the background without blocking the main execution flow.
    """
    await asyncio.sleep(10)
    
    """
    this will call the consume events function from kafka_consumer.py file to consume the subscribed 
    customer topic against the customer consumer group id and handle all the customer related db operation in consumer
    """
    asyncio.create_task(
        consume_events(config.KAFKA_CUSTOMER_TOPIC, config.KAFKA_CUSTOMER_CONSUMER_GROUP_ID)
    )
    
    """
    this will call the consume events function from kafka_consumer.py file to consume the subscribed 
    user topic against the user consumer group id and handle all the user related db operation in consumer
    """
    asyncio.create_task(
        consume_events(config.KAFKA_USER_TOPIC, config.KAFKA_USER_CONSUMER_GROUP_ID)
    )
    
    """
    this will call the consume events function from kafka_consumer.py file to consume the subscribed
    product topic against the product consumer group id and handle all the product related db operation in consumer
    """
    asyncio.create_task(
        consume_events(
            config.KAFKA_PRODUCT_TOPIC, config.KAFKA_PRODUCT_CONSUMER_GROUP_ID
        )
    )
    
    """
    this will call the consume events function from kafka_consumer.py file to consume the subscribed 
    category topic against the category consumer group id and handle all the category related db operation in consumer
    """
    asyncio.create_task(
        consume_events(
            config.KAFKA_CATEGORY_TOPIC, config.KAFKA_CATEGORY_CONSUMER_GROUP_ID
        )
    )
    
    """
    this will call the consume events function from kafka_consumer.py file to consume the subscribed 
    brand topic against the brand consumer group id and handle all the brand related db operation in consumer
    """
    asyncio.create_task(
        consume_events(config.KAFKA_BRAND_TOPIC, config.KAFKA_BRAND_CONSUMER_GROUP_ID)
    )
    
    """
    this will call the consume events function from kafka_consumer.py file to consume the subscribed
    order topic against the order consumer group id and handle all the order related db operation in consumer
    """
    asyncio.create_task(
        consume_events(config.KAFKA_ORDER_WITH_DETAIL_TOPIC, config.KAFKA_ORDER_CONSUMER_GROUP_ID)
    )

    """
    This allows the `run_alembic_upgrade()` function to be executed asynchronously 
    and create db schema using alembic database migration script
    """
    asyncio.create_task(run_alembic_upgrade())

    yield


app = FastAPI(lifespan=lifespan, title="Hello World db service API")


"""
This will include all the routes defined in router directory
"""
app.include_router(user_router.router)
app.include_router(product_router.router)
app.include_router(category_router.router)
app.include_router(brand_router.router)
app.include_router(order_router.router)
app.include_router(payment_router.router)
app.include_router(customer_router.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


"""test end point to execute db migration manually"""
@app.get("/dbup")
async def dbup():
    try:
        await run_alembic_upgrade()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
