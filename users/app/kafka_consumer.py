import json
import sys
from aiokafka import AIOKafkaConsumer
from fastapi import HTTPException  # type: ignore
from app import config
import os
from datetime import datetime

responses = {}


async def consume_response_from_kafka(consumer, request_id):
    # count=0
    async for msg in consumer:
        # if(count>50):
        #    break
        # count = count+1
        response = json.loads(msg.value.decode("utf-8"))
        status = response.get("status").get("status")

        message = "Operation failed"
        
        if response.get("request_id") == request_id:
            if status == "success":
                message = "User created successfully"
            elif status == "duplicate":
                message = "Record already exists"
            elif status == "exist":
                message = "User already exists"
            elif status == "failed":
                message = "Failed to create user"
            elif status == "not-found":
                message = "User not found"
            elif status == "success-update":
                message = "User update successfully"
            elif status == "failed-update":
                message = "Failed to update user"
            elif status == "success-delete":
                message = "User deleted successfully"
            elif status == "failed-delete":
                message = "Failed to delete user"

            return {"message": message}
        # raise HTTPException(status_code=500, detail="No response from db-service")


async def get_kafka_consumer():
    consumer = AIOKafkaConsumer(
        config.KAFKA_USER_DB_RESPONSE,
        bootstrap_servers=str(config.BOOTSTRAP_SERVER),
        group_id=config.KAFKA_USER_CONSUMER_GROUP_ID,
        auto_offset_reset="earliest",
    )
    await consumer.start()
    return consumer


# async def get_kafka_consumer_1():
#     consumer = AIOKafkaConsumer(
#         config.KAFKA_USER_DB_RESPONSE,
#         bootstrap_servers=str(config.BOOTSTRAP_SERVER),
#         group_id=config.KAFKA_USER_CONSUMER_GROUP_ID,
#         auto_offset_reset="earliest",
#     )
#     await consumer.start()
#     try:
#         yield consumer
#     finally:
#         await consumer.stop()


# async def consume_events(topic):
#     # Create a consumer instance.
#     consumer = AIOKafkaConsumer(
#         topic,
#         bootstrap_servers=str(config.BOOTSTRAP_SERVER),
#         group_id=config.KAFKA_USER_CONSUMER_GROUP_ID,
#         auto_offset_reset="earliest",
#     )

#     # Start the consumer.
#     await consumer.start()

#     async for message in consumer:
#         #response = message.value.decode()
#         response = json.loads(message.value.decode("utf-8"))
#         responses[response['uuid']] = response["status"]
#         log_message(response, message.topic)

#     # async for message in consumer:
#     #     try:
#     #         filename = "example.txt"
#     #         # Continuously listen for messages.

#     #         print(
#     #             f"Received message: {message.value.decode()} on topic {message.topic}"
#     #         )

#     #         content = (
#     #             f"{datetime.now().time()}  - Received message: {message.value.decode()} on topic {message.topic}"
#     #         )

#     #         write_to_file(filename, content)
#     #         # Here you can add code to process each message.
#     #         # Example: parse the message, store it in a database, etc.
#     #     finally:
#     #         # Ensure to close the consumer when done.
#     #         await consumer.stop()


# def log_message(entity_data, topic):
#     # print(f"Received message: {message.value.decode()} on topic {message.topic}")
#     # content = f"{datetime.now().time()}  - Received message: {entity_data} on topic {message.topic} and dbuser is {db_user}"

#     filename = "example.txt"
#     content = (
#         f"{datetime.now().time()}  - Received message: {entity_data} on topic {topic}"
#     )
#     write_to_file(filename, content)

# def write_to_file(filename, content):
#     # Check if the file exists
#     if os.path.exists(filename):
#         # Open the file in append mode
#         with open(filename, "a") as file:
#             file.write(content + "\n")
#     else:
#         # Create a new file and write to it
#         with open(filename, "w") as file:
#             file.write(content + "\n")
