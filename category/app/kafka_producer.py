from aiokafka import AIOKafkaProducer  # type: ignore
from app import config


async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=str(config.BOOTSTRAP_SERVER))
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
