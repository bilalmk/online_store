from datetime import datetime
from decimal import Decimal
import json
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from aiohttp import ClientSession, TCPConnector
from fastapi import APIRouter, FastAPI, Depends, File, Form, HTTPException, UploadFile
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
from shared.models.order_detail_model import CreateOrderWithDetail, PublicOrderWithDetail
from shared.models.token import  TokenData


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("starting lifespan process")
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
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super(CustomJSONEncoder, self).default(obj)


@router.post("/create")
async def create(
    order: CreateOrderWithDetail,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    token: Annotated[TokenData, Depends(get_token)]
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
        # await asyncio.sleep(10)
    except Exception as e:
        return str(e)

    consumer = await get_kafka_consumer()
    try:
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

@router.get("/order/{order_id}", response_model=PublicOrder)
async def read_order_by_id(order_id:str):
    order = await get_order(order_id)
    return order

# @router.patch("/update/{product_guid_id}")
# async def update_product(
#     product: UpdateProduct,
#     product_guid_id: str,
#     producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
#     token: Annotated[TokenData, Depends(get_token)],
# ):
#     product_data = product.model_dump(exclude_unset=True)
    
#     message = {
#         "request_id": product_guid_id,
#         "operation": "update",
#         "entity": "product",
#         "data": product_data,
#     }

#     obj = json.dumps(message).encode("utf-8")
#     await producer.send(config.KAFKA_PRODUCT_TOPIC, value=obj)

#     consumer = await get_kafka_consumer()
#     try:
#         status_message = await consume_response_from_kafka(consumer, product_guid_id)
#     finally:
#         await consumer.stop()

#     if status_message:
#         return status_message

#     status_message = {"message": "Try again"}
#     return status_message


# @router.delete("/delete/{order_guid_id}")
# async def delete_order(
#     order_guid_id: str,
#     producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
#     token: Annotated[TokenData, Depends(get_token)],
# ):
#     try:
#         message = {
#             "request_id": order_guid_id,
#             "operation": "delete",
#             "entity": "order",
#             "data": {},
#         }

#         obj = json.dumps(message).encode("utf-8")
#         await producer.send(config.KAFKA_ORDER_TOPIC, value=obj)

#         consumer = await get_kafka_consumer()
#         try:
#             status_message = await consume_response_from_kafka(consumer, order_guid_id)
#         finally:
#             await consumer.stop()

#         if status_message:
#             return status_message

#         status_message = {"message": "Try again"}
#         return status_message

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/", response_model=list[PublicOrder])
# async def get_products(token: Annotated[TokenData, Depends(get_token)]):
#     orders = await get_order_list(token.user_id)
#     return orders



app.include_router(router)
