from datetime import datetime
import json
import asyncio
import sys
from aiokafka import AIOKafkaConsumer  # type: ignore
from app import config
import os

from app.operations import insert_payment

responses = {}

# async def consume_events_order(topic, group_id):
#     # Create a consumer instance.
#     consumer = AIOKafkaConsumer(
#         topic,
#         bootstrap_servers=str(config.BOOTSTRAP_SERVER),
#         group_id=group_id,
#         auto_offset_reset="earliest",
#     )

#     # Start the consumer.
#     await consumer.start()
#     try:
#         # Continuously listen for messages.
#         async for message in consumer:
#             pass
#     finally:
#         # Ensure to close the consumer when done.
#         await consumer.stop()

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
    # print(f"Received message: {message.value.decode()} on topic {message.topic}")
    # content = f"{datetime.now().time()}  - Received message: {entity_data} on topic {message.topic} and dbuser is {db_user}"

    filename = "example.txt"
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

# async def consume_response_from_kafka(consumer, request_id):
#     message_count = 0
#     while True:
#         try:
#             message = await asyncio.wait_for(consumer.getone(), timeout=5)
        
#             response = json.loads(message.value.decode("utf-8"))
#             status = response.get("status").get("status")

#             message = "Operation failed"

#             if response.get("request_id") == request_id:
#                 if status == "success":
#                     message = "Product created successfully"
#                 elif status == "duplicate":
#                     message = "Product already exists"
#                 elif status == "exist":
#                     message = "Product already exists"
#                 elif status == "failed":
#                     message = "Failed to create product"
#                 elif status == "not-found":
#                     message = "Product not found"
#                 elif status == "success-update":
#                     message = "Product update successfully"
#                 elif status == "failed-update":
#                     message = "Failed to update product"
#                 elif status == "success-delete":
#                     message = "Product deleted successfully"
#                 elif status == "failed-delete":
#                     message = "Failed to delete product"

#                 return {"message": message}
#         except asyncio.TimeoutError:
#             return {"message": "No messages received."}
#             break  # or continue, based on your use case


async def get_kafka_consumer():
    consumer = AIOKafkaConsumer(
        config.KAFKA_PAYMENTS_DB_RESPONSE,
        bootstrap_servers=str(config.BOOTSTRAP_SERVER),
        group_id=config.KAFKA_PAYMENT_CONSUMER_GROUP_ID,
        auto_offset_reset="earliest",
    )
    await consumer.start()
    return consumer
