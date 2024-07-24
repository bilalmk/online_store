import json
import asyncio
import sys
from aiokafka import AIOKafkaConsumer  # type: ignore
from app import config
from app.kafka_producer import get_kafka_producer
from shared.models.inventory import InventoryProductUpdate
from shared.models.order_detail_model import PublicOrderWithDetail

responses = {}

async def consume_events(topic, group_id):
    """
    This function asynchronously consumes messages from a Kafka topic, processes the
    data, and produces an inventory update if applicable.
    """
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
            response = json.loads(message.value.decode("utf-8"))
            request_id = response.get("request_id")
            data = response.get("data")
            order_information = data.get("order_information")

            """ send data to produce the product topic if valid order information is available"""
            if order_information:
                await produce_inventory_update(order_information)
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()


async def produce_inventory_update(order_information: PublicOrderWithDetail):
    """
    This produces an inventory update message for a given order information using
    Kafka producer.
    
    order_information object contain information about an order along
    with its details. we extracts the order details, creates inventory update information
    based on the product ID and quantity from the order details and produce it to product 
    topic to be consumed by product microservice and update the inventory according to the
    product used in order
    """
    order_details = order_information.get("order_details")
    inventory_update_info = [{"product_id": info.get("product_id"), "quantity": info.get("quantity")} for info in order_details]
    message = {
        "request_id": order_information.get("order_id"),
        "operation": "update",
        "entity": "product",
        "data": {"inventory_info": inventory_update_info},
    }

    try:
        async with get_kafka_producer() as producer:
            obj = json.dumps(message).encode("utf-8")
            await producer.send(config.KAFKA_INVENTORY_TOPIC, value=obj)
        # await asyncio.sleep(10)
    except Exception as e:
        print(str(e))
        sys.stdout.flush()
        return str(e)
