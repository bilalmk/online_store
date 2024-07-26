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
from app.operation.customer_operation import CustomerOperation


async def consume_events(topic, group_id):
    """
    The function consumes messages from a Kafka consumer and process the response based on the topic value.
    select the correct operation class on the basis of topic value.
    
    All microservices in the system are producing their data to kafka topics for db operations and this consumer of db-service
    is consuming the messages from topic and sending the data to the respective classes for db crud operations
    
    :topic: name of topic which is used my consumer to consumed the messages
    :group_id: name of group, topics are subscribed for
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
            # create user
            data = json.loads(message.value.decode("utf-8"))
            if message.topic == "customers":
                t = CustomerOperation(data)
                await t.operations()
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

            # log_message(data.get("data"), message.topic)

    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()


""" Create a log message function to log the errors in text bases log files"""
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
