from aiokafka import AIOKafkaConsumer  # type: ignore
from app import config
import os
from datetime import datetime

async def consume_response_from_kafka(consumer, request_id):
    async for msg in consumer:
        response = msg.value.decode()
        if response.get('request_id') == request_id:
            if response.get('status') == 'success':
                print("Request inserted into DB successfully.")
            elif response.get('status') == 'duplicate':
                print("Record already exists.")
            else:
                print("Failed to insert request into DB.")
            break
        
        
async def get_kafka_consumer(topic):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=config.BOOTSTRAP_SERVER,
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
        bootstrap_servers=config.BOOTSTRAP_SERVER,
        group_id=config.KAFKA_USER_CONSUMER_GROUP_ID,
        auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        filename = "example.txt"
        # Continuously listen for messages.
            
        print(
            f"Received message: {message.value.decode()} on topic {message.topic}"
        )
        
        content = (
            f"{datetime.now().time()}  - Received message: {message.value.decode()} on topic {message.topic}"
        )

        write_to_file(filename, content)
        # Here you can add code to process each message.
        # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()


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
