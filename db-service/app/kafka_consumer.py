import json
from aiokafka import AIOKafkaConsumer  # type: ignore
from app import config
from app.config import get_session
import os
from datetime import datetime

from app.crud.user_crud import User_Crud
from shared.models.user import CreateUser


async def consume_events(topic, group_id):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=config.BOOTSTRAP_SERVER,
        group_id=group_id,
        auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        filename = "example.txt"
        # Continuously listen for messages.
        async for message in consumer:
            # create user
            data = json.loads(message.value.decode('utf-8'))
            operation = data.get("operation")
            entity_data = data.get("data")
            
            content = (
                f"{datetime.now().time()}  - Received message:{entity_data}  on topic {message.topic}"
            )

            write_to_file(filename, content)
            
            if operation == 'create':
                # Handle create operation
                with get_session() as session:
                    hero_crud = User_Crud(session)
                    hero_crud.create_user(CreateUser(**entity_data))
                print(f"Creating user: {entity_data}")
            elif operation == 'update':
                # Handle update operation
                print(f"Updating user: {entity_data}")
            elif operation == 'delete':
                # Handle delete operation
                print(f"Deleting user: {entity_data}")
            
            
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
