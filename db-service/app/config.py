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

sessionDep = Annotated[Session, Depends(get_session)]

BOOTSTRAP_SERVER = os.environ.get("BOOTSTRAP_SERVER")
KAFKA_USER_TOPIC = os.environ.get("KAFKA_USER_TOPIC")
KAFKA_PRODUCT_TOPIC = os.environ.get("KAFKA_PRODUCT_TOPIC")
KAFKA_PRODUCT_CONSUMER_GROUP_ID = os.environ.get("KAFKA_PRODUCT_CONSUMER_GROUP_ID")
KAFKA_USER_CONSUMER_GROUP_ID = os.environ.get("KAFKA_USER_CONSUMER_GROUP_ID")
KAFKA_USER_DB_RESPONSE = os.environ.get("KAFKA_USER_DB_RESPONSE")