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
from fastapi.exceptions import RequestValidationError
from aiokafka import AIOKafkaProducer  # type: ignore
from app.kafka_producer import get_kafka_producer
from app.kafka_consumer import (
    get_kafka_consumer,
    consume_response_from_kafka,
)

from app import config
from app.operations import get_token, get_category_list, get_category
from app.exceptions.handler import http_exception_handler, validation_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException

from shared.models.category import (
    CreateCategory,
    PublicCategory,
    UpdateCategory,
)
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

""" handlers to parse the error before send to user """
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore
# app.add_middleware(ExceptionHandlingMiddleware)

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    dependencies=[Depends(get_token)],
    responses={404: {"description": "Not found"}},
)


@app.get("/")
def check():
    return {"message": "Hello World from categories"}


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
- Endpoint to create a new category
- produce data to kafka topic, this topic is consumed by db-service
- db-service will produce response to kafka topic, this topic is consumed back by this api
- consumed response will be sent back to the caller
"""
@router.post("/create")
async def create(
    category: CreateCategory,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
):
    category_dict = category.dict()

    message = {
        "request_id": category.guid,
        "operation": "create",
        "entity": "category",
        "data": category_dict,
    }

    try:
        """
        get response back of create category end point of db-service, 
        responsible to get topic data, perform db operation and sent status back to caller
        """
        obj = json.dumps(message, cls=CustomJSONEncoder).encode("utf-8")
        await producer.send(config.KAFKA_CATEGORY_TOPIC, value=obj)
        # await asyncio.sleep(10)
    except Exception as e:
        return str("e")

    consumer = await get_kafka_consumer()
    try:
        status_message = await consume_response_from_kafka(consumer, category.guid)
    finally:
        await consumer.stop()

    if status_message:
        return status_message

    status_message = {"message": "Created"}
    return status_message


"""
- this endpoint is protected and can only be accessed by authenticated system users
- this endpoint is responsible to update the category data
- this endpoint produce the data to kafka topic, this topic is consumed by db-service
- db-service will produce response to kafka topic, this topic is consumed back by this api
- consumed response will be sent back to the caller
"""
@router.patch("/update/{category_guid_id}")
async def update_category(
    category: UpdateCategory,
    category_guid_id: str,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
):

    try:
        category_data = category.model_dump(exclude_unset=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not category_data:
        raise HTTPException(status_code=400, detail="No data provided")

    message = {
        "request_id": category_guid_id,
        "operation": "update",
        "entity": "category",
        "data": category_data,
    }

    obj = json.dumps(message).encode("utf-8")
    await producer.send(config.KAFKA_CATEGORY_TOPIC, value=obj)

    consumer = await get_kafka_consumer()
    try:
        """
        get response back from db-service, 
        db-service is responsible to collect topic data 
        perform db operation and produce response data to kafka topic        
        """
        status_message = await consume_response_from_kafka(consumer, category_guid_id)
    finally:
        await consumer.stop()

    if status_message:
        return status_message

    status_message = {"message": "Try again"}
    return status_message


"""
- this endpoint is protected and can only be accessed by authenticated system users
- Endpoint is use to soft delete the category from db
- this endpoint produce the data to kafka topic, this topic is consumed by db-service
- db-service will produce response to kafka topic, kafka topic is consumed back by this api
- consumed response will be sent back to the caller
"""
@router.delete("/delete/{category_guid_id}")
async def delete_category(
    category_guid_id: str,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
):
    try:
        message = {
            "request_id": category_guid_id,
            "operation": "delete",
            "entity": "category",
            "data": {},
        }

        obj = json.dumps(message).encode("utf-8")
        await producer.send(config.KAFKA_CATEGORY_TOPIC, value=obj)

        consumer = await get_kafka_consumer()
        try:
            status_message = await consume_response_from_kafka(
                consumer, category_guid_id
            )
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
- call get_category_list function from operation file
- Retrieves a list of categories and returns it as a response.
"""
@router.get("/", response_model=list[PublicCategory])
async def get_categories():
    list = await get_category_list()
    return list

"""
- This endpoint is protected and can only be accessed by authenticated system users
- call get_category function from operation file
- Retrieves and return a category data, based on provided category id.
"""
@router.get("/category/{category_id}", response_model=PublicCategory)
async def read_category_by_id(category_id: int):
    category = await get_category(category_id)
    return category


app.include_router(router)
