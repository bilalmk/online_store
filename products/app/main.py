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
from app.operations import get_token
from shared.models.product import CreateProduct, Product, UpdateProduct
from shared.models.token import Token, TokenData


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("starting lifespan process")
    config.client_session = ClientSession(connector=TCPConnector(limit=100))
    yield
    await config.client_session.close()


app = FastAPI(lifespan=lifespan, title="Hello World API with DB")

router = APIRouter(
    prefix="/products",
    tags=["products"],
    dependencies=[Depends(get_token)],
    responses={404: {"description": "Not found"}},
)


@app.get("/")
def main():
    return {"message": "Hello World from products"}


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super(CustomJSONEncoder, self).default(obj)


@router.post("/create")
async def create(
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    token: Annotated[TokenData, Depends(get_token)],
    name: str = Form(...),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    category_id: int = Form(...),
    brand_id: int = Form(...),
    created_by: int = Form(...),
    status: int = Form(...),
    file: UploadFile = File(None)
):
    product = CreateProduct(
        name=name,
        price=price,
        stock_quantity=stock_quantity,
        category_id=category_id,
        brand_id=brand_id,
        created_by=token.userid,
        status=status
    )
    
    if file:
        product.image_name = f"{product.guid}_{file.filename}"
        
    product_dict = product.dict()

    message = {
        "request_id": product.guid,
        "operation": "create",
        "entity": "product",
        "data": product_dict,
    }

    try:
        obj = json.dumps(message, cls=CustomJSONEncoder).encode("utf-8")
        await producer.send(config.KAFKA_PRODUCT_TOPIC, value=obj)
        # await asyncio.sleep(10)
    except Exception as e:
        return str(e)

    consumer = await get_kafka_consumer()
    try:
        status_message = await consume_response_from_kafka(consumer, product.guid)
    finally:
        await consumer.stop()

    if status_message:
        if file:
            await save_file(file, product.guid)
        return status_message

    status_message = {"message": "Created"}
    return status_message


@router.patch("/update/{product_guid_id}")
async def update_product(
    product: UpdateProduct,
    product_guid_id: str,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    token: Annotated[TokenData, Depends(get_token)],
):
    product_data = product.model_dump(exclude_unset=True)
    
    message = {
        "request_id": product_guid_id,
        "operation": "update",
        "entity": "product",
        "data": product_data,
    }

    obj = json.dumps(message).encode("utf-8")
    await producer.send(config.KAFKA_PRODUCT_TOPIC, value=obj)

    consumer = await get_kafka_consumer()
    try:
        status_message = await consume_response_from_kafka(consumer, product_guid_id)
    finally:
        await consumer.stop()

    if status_message:
        return status_message

    status_message = {"message": "Try again"}
    return status_message


@router.delete("/delete/{product_guid_id}")
async def delete_product(
    product_guid_id: str,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    token: Annotated[TokenData, Depends(get_token)],
):
    try:
        message = {
            "request_id": product_guid_id,
            "operation": "delete",
            "entity": "product",
            "data": {},
        }

        obj = json.dumps(message).encode("utf-8")
        await producer.send(config.KAFKA_PRODUCT_TOPIC, value=obj)

        consumer = await get_kafka_consumer()
        try:
            status_message = await consume_response_from_kafka(consumer, product_guid_id)
        finally:
            await consumer.stop()

        if status_message:
            return status_message

        status_message = {"message": "Try again"}
        return status_message

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def save_file(file: UploadFile, product_guid: str | None):
    file_location = f"./upload_images/{product_guid}_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    return {"file_path": file_location}


app.include_router(router)
