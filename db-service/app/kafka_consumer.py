import json
import sys
from aiokafka import AIOKafkaConsumer  # type: ignore
from app import config
import os
from datetime import datetime
from app.operation.product_operation import ProductOperation
from app.operation.user_operation import UserOperation
from app.operation.category_operation import CategoryOperation
from app.operation.brand_operation import BrandOperation
from app.operation.order_operation import OrderOperation


async def consume_events(topic, group_id):
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
            # create user
            data = json.loads(message.value.decode("utf-8"))
            if message.topic == "users":
                t = UserOperation(data)
                await t.operations()
            if message.topic == "products":
                t = ProductOperation(data)
                await t.operations()
            if message.topic == "category":
                t = CategoryOperation(data)
                await t.operations()
            if message.topic == "brands":
                t = BrandOperation(data)
                await t.operations()
            if message.topic == "order_with_detail":
                t = OrderOperation(data)
                await t.operations()

            #log_message(data.get("data"), message.topic)

            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
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
