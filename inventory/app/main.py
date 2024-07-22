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
    print("starting lifespan process")
    config.client_session = ClientSession(connector=TCPConnector(limit=100))

    await asyncio.sleep(10)
    asyncio.create_task(
        consume_events(
            config.KAFKA_NOTIFICATION_TOPIC, config.KAFKA_INVENTORY_CONSUMER_GROUP_ID
        )
    )

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


@app.post("/inventory_update")
async def inventory_update(order_information: PublicOrderWithDetail):
    # print("inventory update route")
    # print(order_information)
    await produce_inventory_update(order_information)
    return {"message": "Inventory updated"}
