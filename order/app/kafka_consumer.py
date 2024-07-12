import json
import asyncio
from aiokafka import AIOKafkaConsumer  # type: ignore
from app import config

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
                    message = "Order created successfully"
                elif status == "duplicate":
                    message = "Order already exists"
                elif status == "exist":
                    message = "Order already exists"
                elif status == "failed":
                    message = "Failed to create order"
                elif status == "not-found":
                    message = "Order not found"
                elif status == "success-update":
                    message = "Order update successfully"
                elif status == "failed-update":
                    message = "Failed to update order"
                elif status == "success-delete":
                    message = "Order deleted successfully"
                elif status == "failed-delete":
                    message = "Failed to delete order"

                return {"message": message}
        except asyncio.TimeoutError:
            return {"message": "No messages received."}
            break  # or continue, based on your use case


async def get_kafka_consumer():
    consumer = AIOKafkaConsumer(
        config.KAFKA_ORDERS_DB_RESPONSE,
        bootstrap_servers=str(config.BOOTSTRAP_SERVER),
        group_id=config.KAFKA_ORDER_CONSUMER_GROUP_ID,
        auto_offset_reset="earliest",
    )
    await consumer.start()
    return consumer