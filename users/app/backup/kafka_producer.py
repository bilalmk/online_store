from confluent_kafka import Producer
from app import config


def get_kafka_producer():
    producer: Producer = Producer({"bootstrap.servers": config.BOOTSTRAP_SERVER})
    # await producer.start()
    try:
        yield producer
    finally:
        producer.flush()
