from datetime import datetime
from decimal import Decimal
import json
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from aiohttp import ClientSession, TCPConnector
from fastapi import (
    APIRouter,
    FastAPI,
    Depends,
    HTTPException,
)
from aiokafka import AIOKafkaProducer  # type: ignore
from app.kafka_consumer import consume_events, produce_inventory_update

from app import config
from app.operations import get_token

from shared.models.category import (
    CreateCategory,
    PublicCategory,
    UpdateCategory,
)
from shared.models.order_detail_model import PublicOrderWithDetail
from shared.models.token import TokenData
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    The line `config.client_session = ClientSession(connector=TCPConnector(limit=100))` is creating
    an instance of `ClientSession` with a `TCPConnector` that has a limit of 100 connections. This
    is used to manage connections to external services. The `limit=100` parameter sets the maximum number of simultaneous
    connections that can be made using this `ClientSession`. This helps in controlling the number of
    connections and managing resources efficiently when interacting with external services.
    """
    config.client_session = ClientSession(connector=TCPConnector(limit=100))

    await asyncio.sleep(10)
    
    """
    The `asyncio.create_task()` function is used to create a task to run a coroutine concurrently in
    the background without blocking the main execution flow.
    
    this will call the consume events function from kafka_consumer.py file to consume the subscribed 
    notification topic against the inventory consumer group id
    """
    asyncio.create_task(
        consume_events(
            config.KAFKA_NOTIFICATION_TOPIC, config.KAFKA_INVENTORY_CONSUMER_GROUP_ID
        )
    )

    """
    this will call the consume events function from kafka_consumer.py file to consume the subscribed 
    inventory topic against the inventory consumer group id
    """
    asyncio.create_task(
        consume_events(
            config.KAFKA_INVENTORY_TOPIC, config.KAFKA_INVENTORY_CONSUMER_GROUP_ID
        )
    )

    yield
    await config.client_session.close()


app = FastAPI(lifespan=lifespan, title="Hello World API with DB")

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(get_token)],
    responses={404: {"description": "Not found"}},
)


@app.get("/")
def check():
    return {"message": "Hello World from notification"}


"""
- this endpoint is protected and can only be accessed by authenticated customer
- this endpoint is responsible to update the inventory data after completing the order process
- this endpoint will call produce_inventory_update from kafka_consumer.py 
- this end-point created just for testing purpose, in real world scenario produce_inventory_update() function
    will be invoked from kafka_consumer.py
- inside kafka consumer the message will be consumed from kafka topic, extract the data and produce to
  another kafka topic to be consumed by product microservice to update the inventory
"""
@app.post("/inventory_update")
async def inventory_update(order_information: PublicOrderWithDetail):
    # print("inventory update route")
    # print(order_information)
    await produce_inventory_update(order_information)
    return {"message": "Inventory updated"}
