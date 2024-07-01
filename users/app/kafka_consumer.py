import json
import sys
from aiokafka import AIOKafkaConsumer
from fastapi import HTTPException  # type: ignore
from app import config
import os
from datetime import datetime
responses = {}
async def consume_response_from_kafka(consumer, request_id):
    async for msg in consumer:
        response = msg.value.decode()
        print(response.get("message"))
        if response.get('request_id') == request_id:
            if response.get('status') == 'success':
                return {"message": "Request inserted into DB successfully"}
            elif response.get('status') == 'duplicate':
                return {"message": "Record already exists."}
            elif response.get('status') == 'failed':
                return {"message": "Failed to insert request into DB."}
            else:
                raise HTTPException(status_code=400, detail="Failed to create user")
                break
    raise HTTPException(status_code=500, detail="No response from db-service")
        
async def get_kafka_consumer():
    consumer = AIOKafkaConsumer(
        config.KAFKA_USER_DB_RESPONSE,
        bootstrap_servers=str(config.BOOTSTRAP_SERVER),
        group_id=config.KAFKA_USER_CONSUMER_GROUP_ID,
        auto_offset_reset="earliest",
    )
    await consumer.start()
    try:
        yield consumer
    finally:
        await consumer.stop()

async def consume_events(topic):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=str(config.BOOTSTRAP_SERVER),
        group_id=config.KAFKA_USER_CONSUMER_GROUP_ID,
        auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    
    async for message in consumer:
        #response = message.value.decode()
        response = json.loads(message.value.decode("utf-8"))
        responses[response['uuid']] = response["status"]
        log_message(response, message.topic)
        
    # async for message in consumer:
    #     try:
    #         filename = "example.txt"
    #         # Continuously listen for messages.
                
    #         print(
    #             f"Received message: {message.value.decode()} on topic {message.topic}"
    #         )
            
    #         content = (
    #             f"{datetime.now().time()}  - Received message: {message.value.decode()} on topic {message.topic}"
    #         )

    #         write_to_file(filename, content)
    #         # Here you can add code to process each message.
    #         # Example: parse the message, store it in a database, etc.
    #     finally:
    #         # Ensure to close the consumer when done.
    #         await consumer.stop()


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
