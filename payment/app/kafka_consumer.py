from datetime import datetime
import json
from aiokafka import AIOKafkaConsumer  # type: ignore
from app import config
import os

from app.operations import insert_payment

responses = {}

async def consume_events_payment(topic, group_id):
    """
    This function asynchronously consumes messages from a Kafka topic, processes the
    data, and call insert_payment() function from operation to record the payment information in database.
    """
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=str(config.BOOTSTRAP_SERVER),
        group_id=group_id,
        auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            payload = json.loads(message.value.decode("utf-8"))
            request_id = payload.get("request_id")
            data = payload.get("data")
            await insert_payment(data)
            
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()


def log_message(entity_data, topic):
    filename = "log.txt"
    content = (
        f"{datetime.now().time()}  - Received message: {entity_data} on topic {topic}"
    )
    write_to_file(filename, content)


def write_to_file(filename, content):
    # Check if the file exists
    if os.path.exists(filename):
        # Open the file in append mode
        with open(filename, "a") as file:
            file.write(content + "\n")
    else:
        # Create a new file and write to it
        with open(filename, "w") as file:
            file.write(content + "\n")

async def get_kafka_consumer():
    consumer = AIOKafkaConsumer(
        config.KAFKA_PAYMENTS_DB_RESPONSE,
        bootstrap_servers=str(config.BOOTSTRAP_SERVER),
        group_id=config.KAFKA_PAYMENT_CONSUMER_GROUP_ID,
        auto_offset_reset="earliest",
    )
    await consumer.start()
    return consumer
