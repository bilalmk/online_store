import os
from typing import Annotated
from dotenv import load_dotenv
from fastapi import Depends
from sqlmodel import Session, create_engine
from contextlib import contextmanager
load_dotenv()

connection = os.environ.get("CONNECTION")
engine = create_engine(connection)  # type: ignore

@contextmanager
def get_session():
    with Session(engine) as session:
        yield session
        
def get_session_new():
    with Session(engine) as session:
        yield session

sessionDep = Annotated[Session, Depends(get_session_new)]

BOOTSTRAP_SERVER = os.environ.get("BOOTSTRAP_SERVER")
KAFKA_USER_TOPIC = os.environ.get("KAFKA_USER_TOPIC")
KAFKA_PRODUCT_TOPIC = os.environ.get("KAFKA_PRODUCT_TOPIC")
KAFKA_CATEGORY_TOPIC = os.environ.get("KAFKA_CATEGORY_TOPIC")
KAFKA_BRAND_TOPIC = os.environ.get("KAFKA_BRAND_TOPIC")
KAFKA_ORDER_TOPIC = os.environ.get("KAFKA_ORDER_TOPIC")
KAFKA_ORDER_WITH_DETAIL_TOPIC = os.environ.get("KAFKA_ORDER_WITH_DETAIL_TOPIC")
KAFKA_ORDER_DETAIL_TOPIC = os.environ.get("KAFKA_ORDER_DETAIL_TOPIC")
KAFKA_CUSTOMER_TOPIC = os.environ.get("KAFKA_CUSTOMER_TOPIC")


KAFKA_PRODUCT_CONSUMER_GROUP_ID = os.environ.get("KAFKA_PRODUCT_CONSUMER_GROUP_ID")
KAFKA_USER_CONSUMER_GROUP_ID = os.environ.get("KAFKA_USER_CONSUMER_GROUP_ID")
KAFKA_CATEGORY_CONSUMER_GROUP_ID = os.environ.get("KAFKA_CATEGORY_CONSUMER_GROUP_ID")
KAFKA_BRAND_CONSUMER_GROUP_ID = os.environ.get("KAFKA_BRAND_CONSUMER_GROUP_ID")
KAFKA_ORDER_CONSUMER_GROUP_ID = os.environ.get("KAFKA_ORDER_CONSUMER_GROUP_ID")
KAFKA_CUSTOMER_CONSUMER_GROUP_ID = os.environ.get("KAFKA_CUSTOMER_CONSUMER_GROUP_ID")


KAFKA_USER_DB_RESPONSE = os.environ.get("KAFKA_USER_DB_RESPONSE")
KAFKA_PRODUCTS_DB_RESPONSE = os.environ.get("KAFKA_PRODUCTS_DB_RESPONSE")
KAFKA_CATEGORY_DB_RESPONSE = os.environ.get("KAFKA_CATEGORY_DB_RESPONSE")
KAFKA_BRAND_DB_RESPONSE = os.environ.get("KAFKA_BRAND_DB_RESPONSE")
KAFKA_ORDERS_DB_RESPONSE = os.environ.get("KAFKA_ORDERS_DB_RESPONSE")
KAFKA_CUSTOMER_DB_RESPONSE = os.environ.get("KAFKA_CUSTOMER_DB_RESPONSE")