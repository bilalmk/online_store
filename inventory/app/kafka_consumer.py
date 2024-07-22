import json
import asyncio
import sys
from aiokafka import AIOKafkaConsumer  # type: ignore
from app import config
from app.kafka_producer import get_kafka_producer
from shared.models.inventory import InventoryProductUpdate
from shared.models.order_detail_model import PublicOrderWithDetail

responses = {}


async def consume_response_from_kafka(consumer, request_id):
    message_count = 0
    while True:
        try:
            message = await asyncio.wait_for(consumer.getone(), timeout=5)

            response = json.loads(message.value.decode("utf-8"))
            status = response.get("status").get("status")

            message = "Operation failed"

            if response.get("request_id") == request_id:
                if status == "success":
                    message = "Category created successfully"
                elif status == "duplicate":
                    message = "Category already exists"
                elif status == "exist":
                    message = "Category already exists"
                elif status == "failed":
                    message = "Failed to create category"
                elif status == "not-found":
                    message = "Category not found"
                elif status == "success-update":
                    message = "Category update successfully"
                elif status == "failed-update":
                    message = "Failed to update category"
                elif status == "success-delete":
                    message = "Category deleted successfully"
                elif status == "failed-delete":
                    message = "Failed to delete category"

                return {"message": message}
        except asyncio.TimeoutError:
            return {"message": "No messages received."}
            break  # or continue, based on your use case


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
            response = json.loads(message.value.decode("utf-8"))
            request_id = response.get("request_id")
            data = response.get("data")
            order_information = data.get("order_information")
            await produce_inventory_update(order_information)
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()


async def produce_inventory_update(order_information: PublicOrderWithDetail):
    inventory_update_info = [{"product_id": info.get("product_id"), "quantity": info.get("quantity")}for info in order_information.get("order_details")]
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
