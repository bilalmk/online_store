from aiokafka import AIOKafkaProducer  # type: ignore
from app import config
import json


async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=config.BOOTSTRAP_SERVER)
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
