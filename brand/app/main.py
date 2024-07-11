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
from app.operations import get_token, get_brand_list, get_brand
from shared.models.brand import CreateBrand, PublicBrand, UpdateBrand
from shared.models.token import TokenData
from app.exceptions.handler import validation_exception_handler,http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("starting lifespan process")
    config.client_session = ClientSession(connector=TCPConnector(limit=100))
    yield
    await config.client_session.close()


app = FastAPI(lifespan=lifespan, title="Hello World API with DB")

app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore

router = APIRouter(
    prefix="/brands",
    tags=["brands"],
    dependencies=[Depends(get_token)],
    responses={404: {"description": "Not found"}},
)


@app.get("/")
def main():
    return {"message": "Hello World from brands"}


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super(CustomJSONEncoder, self).default(obj)


@router.post("/create")
async def create(
    brand: CreateBrand,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    token: Annotated[TokenData, Depends(get_token)],
):

    brand_dict = brand.dict()

    message = {
        "request_id": brand.guid,
        "operation": "create",
        "entity": "brand",
        "data": brand_dict,
    }

    try:
        obj = json.dumps(message, cls=CustomJSONEncoder).encode("utf-8")
        await producer.send(config.KAFKA_BRAND_TOPIC, value=obj)
        # await asyncio.sleep(10)
    except Exception as e:
        return str(e)

    consumer = await get_kafka_consumer()
    try:
        status_message = await consume_response_from_kafka(consumer, brand.guid)
    finally:
        await consumer.stop()

    if status_message:
        return status_message

    status_message = {"message": "Created"}
    return status_message


@router.patch("/update/{brand_guid_id}")
async def update_brand(
    brand: UpdateBrand,
    brand_guid_id: str,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    token: Annotated[TokenData, Depends(get_token)],
):
    brand_data = brand.model_dump(exclude_unset=True)

    message = {
        "request_id": brand_guid_id,
        "operation": "update",
        "entity": "brand",
        "data": brand_data,
    }

    obj = json.dumps(message).encode("utf-8")
    await producer.send(config.KAFKA_BRAND_TOPIC, value=obj)

    consumer = await get_kafka_consumer()
    try:
        status_message = await consume_response_from_kafka(consumer, brand_guid_id)
    finally:
        await consumer.stop()

    if status_message:
        return status_message

    status_message = {"message": "Try again"}
    return status_message


@router.delete("/delete/{brand_guid_id}")
async def delete_brand(
    brand_guid_id: str,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    token: Annotated[TokenData, Depends(get_token)],
):
    try:
        message = {
            "request_id": brand_guid_id,
            "operation": "delete",
            "entity": "brand",
            "data": {},
        }

        obj = json.dumps(message).encode("utf-8")
        await producer.send(config.KAFKA_BRAND_TOPIC, value=obj)

        consumer = await get_kafka_consumer()
        try:
            status_message = await consume_response_from_kafka(
                consumer, brand_guid_id
            )
        finally:
            await consumer.stop()

        if status_message:
            return status_message

        status_message = {"message": "Try again"}
        return status_message

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[PublicBrand])
async def get_brands():
    list = await get_brand_list()
    return list


@router.get("/brand/{brand_id}", response_model=PublicBrand)
async def read_brand_by_id(brand_id: int):
    brand = await get_brand(brand_id)
    return brand

app.include_router(router)
