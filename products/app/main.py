import asyncio
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
    consume_events,
    get_kafka_consumer,
    consume_response_from_kafka,
)

from app import config
from app.operations import (
    get_token,
    get_product_list,
    get_product,
    get_categories,
    get_brands,
    get_category_list,
    get_brand_list,
)
from shared.models.product import CreateProduct, PublicProduct, UpdateProduct
from shared.models.token import TokenData


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("starting lifespan process")
    
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
    inventory topic against the product consumer group id
    
    this will ensure that the product quantity in inventory is updated in real time when the order is executed
    """
    asyncio.create_task(
        consume_events(
            config.KAFKA_INVENTORY_TOPIC, config.KAFKA_PRODUCT_CONSUMER_GROUP_ID
        )
    )
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
- This endpoint is protected and can only be accessed by authenticated system user
- Endpoint to create a new product
- produce data to kafka topic, this topic is consumed by db-service
- db-service will produce response to kafka topic, kafka topic is consumed back by this api
- consumed response will be sent back to the caller
- user can upload a single image with product
"""
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
    file: UploadFile = File(None),
):
    product = CreateProduct(
        name=name,
        price=price,
        stock_quantity=stock_quantity,
        category_id=category_id,
        brand_id=brand_id,
        created_by=token.userid,
        status=status,
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
    except Exception as e:
        return str(e)

    consumer = await get_kafka_consumer()
    try:
        """
        get response back of create order end point of db-service, 
        responsible to get topic data, perform db operation and sent status back to caller
        """
        status_message = await consume_response_from_kafka(consumer, product.guid)
    finally:
        await consumer.stop()

    if status_message:
        if file:
            await save_file(file, product.guid)
        return status_message

    status_message = {"message": "Created"}
    return status_message


"""
- this endpoint is protected and can only be accessed by authenticated system users
- this endpoint is responsible to update the product data
- this endpoint produce the data to kafka topic, kafka topic then consumed by db-service
- db-service will produce response to kafka topic, kafa topic then consumed back by this api
- consumed response will be sent back to the caller
"""
@router.patch("/update/{product_guid_id}")
async def update_product(
    product: UpdateProduct,
    product_guid_id: str,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
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
        """
        get response back from db-service, 
        db-service is responsible to collect topic data 
        perform db operation and produce response data to kafka topic        
        """
        status_message = await consume_response_from_kafka(consumer, product_guid_id)
    finally:
        await consumer.stop()

    if status_message:
        return status_message

    status_message = {"message": "Try again"}
    return status_message


"""
- this endpoint is protected and can only be accessed by authenticated system users
- Endpoint is use to soft delete the product from db
- this endpoint produce the data to kafka topic, kafka topic then consumed by db-service
- db-service will produce response to kafka topic, kafka topic then consumed back by this api
- consumed response will be sent back to the caller
"""
@router.delete("/delete/{product_guid_id}")
async def delete_product(
    product_guid_id: str,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
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
            """
            get response back of delete product end point of db-service, 
            responsible to get topic data, perform db operation and sent status back to caller
            """
            status_message = await consume_response_from_kafka(
                consumer, product_guid_id
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
- call get_product_list function from operation file
- Retrieves a list of products and associated categories, brands.
- It then constructs a list of PublicProduct objects with category and brand names and returns it as a response.
"""
@router.get("/", response_model=list[PublicProduct])
async def get_products():
    products = await get_product_list()
    categories = await get_category_list()
    brands = await get_brand_list()

    cat_dict = {cat["id"]: cat["category_name"] for cat in categories}
    brand_dict = {brand["id"]: brand["brand_name"] for brand in brands}

    for product in products:
        product["category_name"] = cat_dict.get(product["category_id"], None)
        product["brand_name"] = brand_dict.get(product["brand_id"], None)
    return products


"""
- This endpoint is protected and can only be accessed by authenticated system users
- call get_product function from operation file
- Retrieves a product and associated categories, brands on provided product id
- It then constructs a PublicProduct objects with category and brand names and returns it as a response.
"""
@router.get("/product/{product_id}", response_model=PublicProduct)
async def read_product_by_id(product_id: int):

    product = await get_product(product_id)
    category = await get_categories(PublicProduct(**product).category_id)
    brand = await get_brands(PublicProduct(**product).brand_id)

    if category and product["category_id"] == category["id"]:
        product["category_name"] = category["category_name"]

    if brand and product["brand_id"] == brand["id"]:
        product["brand_name"] = brand["brand_name"]

    return product


async def save_file(file: UploadFile, product_guid: str | None):
    """
    The function `save_file` saves an uploaded file to a specified location with a filename based on the
    product GUID.
    """
    file_location = f"./upload_images/{product_guid}_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    return {"file_path": file_location}


app.include_router(router)
