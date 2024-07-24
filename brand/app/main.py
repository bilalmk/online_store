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
from app.exceptions.handler import validation_exception_handler, http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
import json

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

""" handlers to parse the error before send to user """
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
- This endpoint is protected and can only be accessed by authenticated system users
- Endpoint to create a new brand
- produce data to kafka topic, this topic is consumed by db-service
- db-service will produce response to kafka topic, kafka topic is consumed back by this api
- consumed response will be sent back to the caller
"""
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
        """
        get response back of create brand end point of db-service, 
        responsible to get topic data, perform db operation and sent status back to caller
        """
        status_message = await consume_response_from_kafka(consumer, brand.guid)
    finally:
        await consumer.stop()

    if status_message:
        return status_message

    status_message = {"message": "Created"}
    return status_message


"""
- this endpoint is protected and can only be accessed by authenticated system users
- this endpoint is responsible to update the brand data
- this endpoint produce the data to kafka topic, kafka topic then consumed by db-service
- db-service will produce response to kafka topic, kafa topic then consumed back by this api
- consumed response will be sent back to the caller
"""
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
        """
        get response back from db-service, 
        db-service is responsible to collect topic data 
        perform db operation and produce response data to kafka topic        
        """
        status_message = await consume_response_from_kafka(consumer, brand_guid_id)
    finally:
        await consumer.stop()

    if status_message:
        return status_message

    status_message = {"message": "Try again"}
    return status_message


"""
- Endpoint is use to soft delete the brand from db
- this endpoint is protected and can only be accessed by authenticated system users
- this endpoint produce the data to kafka topic, kafka topic then consumed by db-service
- db-service will produce response to kafka topic, kafka topic then consumed back by this api
- consumed response will be sent back to the caller
"""
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
            """
            get response back of delete brand end point of db-service, 
            responsible to get topic data, perform db operation and sent status back to caller
            """
            status_message = await consume_response_from_kafka(consumer, brand_guid_id)
        finally:
            await consumer.stop()

        if status_message:
            return status_message

        status_message = {"message": "Try again"}
        return status_message

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
- This endpoint is protected and can only be accessed by authenticated system users
- call get_brand_list function from operation file
- Retrieves a list of brands and returns it as a response.
"""
@router.get("/", response_model=list[PublicBrand])
async def get_brands():
    list = await get_brand_list()
    return list


"""
- This endpoint is protected and can only be accessed by authenticated system users
- call get_brand function from operation file
- Retrieves and return a brand data, based on provided category id.
"""
@router.get("/brand/{brand_id}", response_model=PublicBrand)
async def read_brand_by_id(brand_id: int):
    brand = await get_brand(brand_id)
    return brand


app.include_router(router)
