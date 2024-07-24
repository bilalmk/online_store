from datetime import datetime
from decimal import Decimal
import json
from contextlib import asynccontextmanager
import sys
from typing import Annotated, AsyncGenerator
from aiohttp import ClientSession, TCPConnector
from fastapi import (
    APIRouter,
    FastAPI,
    Depends,
    HTTPException,
)
from aiokafka import AIOKafkaProducer  # type: ignore
from app.kafka_consumer import consume_events, send_email

from app import config
from app.operations import get_token

from shared.models.category import (
    CreateCategory,
    PublicCategory,
    UpdateCategory,
)
from shared.models.notification import CreateNotification
from shared.models.token import TokenData
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("starting lifespan process")
    config.client_session = ClientSession(connector=TCPConnector(limit=100))

    await asyncio.sleep(10)
    """
    The `asyncio.create_task()` function is used to create a task to run a coroutine concurrently in
    the background without blocking the main execution flow.
    
    this will call the consume events function from kafka_consumer.py file to consume the subscribed 
    notification topic against the notification consumer group id
    """
    asyncio.create_task(
        consume_events(config.KAFKA_NOTIFICATION_TOPIC, config.KAFKA_NOTIFICATION_CONSUMER_GROUP_ID)
    )

    yield
    await config.client_session.close()


app = FastAPI(lifespan=lifespan, title="Hello World API with DB")

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    dependencies=[Depends(get_token)],
    responses={404: {"description": "Not found"}},
)

@app.get("/")
def check():
    return {"message": "Hello World from notification"}

"""
    This function sends an email notification using the information provided in the request body
    and handles exceptions by returning an error response if the email sending fails.
    
    this is the testing end point for sending email notification in actual scenario this email notification
    will be send by microservice running in back ground 
"""
@app.post("/send_email")
async def send_notification(info: CreateNotification):
    try:
        await send_email(info)
    except Exception as e:
        print(str(e))
        sys.stdout.flush()
        raise HTTPException(status_code=500, detail=str(e)) from e
    return {"message": "Email sent successfully"}