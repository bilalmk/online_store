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
from shared.models.token import Token, TokenData


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("starting lifespan process")
    config.client_session = ClientSession(connector=TCPConnector(limit=100))
    yield
    await config.client_session.close()


app = FastAPI(lifespan=lifespan, title="Hello World API with DB")

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
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super(CustomJSONEncoder, self).default(obj)


@router.post("/create")
async def create(
    category: CreateCategory,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    token: Annotated[TokenData, Depends(get_token)],
):
    category_dict = category.dict()

    message = {
        "request_id": category.guid,
        "operation": "create",
        "entity": "category",
        "data": category_dict,
    }

    try:
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


@router.patch("/update/{category_guid_id}")
async def update_category(
    category: UpdateCategory,
    category_guid_id: str,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    token: Annotated[TokenData, Depends(get_token)],
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
        status_message = await consume_response_from_kafka(consumer, category_guid_id)
    finally:
        await consumer.stop()

    if status_message:
        return status_message

    status_message = {"message": "Try again"}
    return status_message


@router.delete("/delete/{category_guid_id}")
async def delete_category(
    category_guid_id: str,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    token: Annotated[TokenData, Depends(get_token)],
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


@router.get("/", response_model=list[PublicCategory])
async def get_categories():
    list = await get_category_list()
    return list


@router.get("/category/{category_id}", response_model=PublicCategory)
async def read_category_by_id(category_id: int):
    category = await get_category(category_id)
    return category


app.include_router(router)
