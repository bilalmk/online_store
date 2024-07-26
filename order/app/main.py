from datetime import datetime
from decimal import Decimal
import json
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from aiohttp import ClientSession, TCPConnector
from fastapi import APIRouter, FastAPI, Depends
from aiokafka import AIOKafkaProducer  # type: ignore
from app.kafka_producer import get_kafka_producer
from app.kafka_consumer import (
    get_kafka_consumer,
    consume_response_from_kafka,
)

from app import config
from app.operations import get_order, get_token
from shared.models.order import CreateOrder, Order, PublicOrder
#from shared.models.order_detail import CreateOrderDetail
from shared.models.order_detail_model import CreateOrderWithDetail
from shared.models.token import TokenData


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
    yield
    await config.client_session.close()


app = FastAPI(lifespan=lifespan, title="Hello World API with DB")

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    dependencies=[Depends(get_token)],
    responses={404: {"description": "Not found"}},
)


@app.get("/")
def main():
    return {"message": "Hello World from orders"}


class CustomJSONEncoder(json.JSONEncoder):
    """ 
    CustomJSONEncoder is a custom JSON encoder class that extends the default JSON encoder
    from the Python standard library. It is used to handle special cases when encoding
    objects like Decimal and datetime.
    """
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super(CustomJSONEncoder, self).default(obj)


"""
- This endpoint is protected and can only be accessed by authenticated customer
- Endpoint to create a new order
- produce data to kafka topic, this topic is consumed by db-service
- db-service will produce response to kafka topic, kafka topic is consumed back by this api
- consumed response will be sent back to the caller
"""
@router.post("/create")
async def create(
    order: CreateOrderWithDetail,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
):
    if order.order_details:
        for order_detail in order.order_details:
            order_detail.order_guid = order.guid
    
    order_dict = order.dict()

    message = {
        "request_id": order.guid,
        "operation": "create",
        "entity": "payment",
        "data": order_dict,
    }

    try:
        obj = json.dumps(message, cls=CustomJSONEncoder).encode("utf-8")
        await producer.send(config.KAFKA_ORDER_WITH_DETAIL_TOPIC, value=obj)
    except Exception as e:
        return str(e)

    consumer = await get_kafka_consumer()
    try:
        """
        get response back of create order end point of db-service, 
        responsible to get topic data, perform db operation and sent status back to caller
        """
        status_message = await consume_response_from_kafka(consumer, order.guid)
    finally:
        await consumer.stop()

    if status_message:
        
        order_obj = json.dumps(status_message.get("order")).encode("utf-8")
        await producer.send(config.KAFKA_ORDER_TOPIC, value=order_obj)

        ## produce to payment service, payment service will product to notification        
        return status_message

    status_message = {"message": "Created"}
    return status_message


"""
- This endpoint is protected and can only be accessed by authenticated customer
- call get_order function from operation file
- Retrieves and return a order data, based on provided order id.
"""
@router.get("/order/{order_id}", response_model=PublicOrder)
async def read_order_by_id(order_id: str):
    order = await get_order(order_id)
    return order


app.include_router(router)
