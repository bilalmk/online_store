from aiokafka import AIOKafkaProducer  # type: ignore
from app import config
import json


async def send_producer(topic, object):
    producer = AIOKafkaProducer(bootstrap_servers=str(config.BOOTSTRAP_SERVER))
    await producer.start()
    await producer.send(topic, object)
    await producer.stop()


async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=str(config.BOOTSTRAP_SERVER))
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
