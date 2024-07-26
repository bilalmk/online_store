import json
import asyncio
from aiokafka import AIOKafkaConsumer  # type: ignore
from app import config
from app.operations import update_product_inventory

responses = {}


async def consume_response_from_kafka(consumer, request_id):
    """
    The function consumes messages from a Kafka consumer and process the response based on the status
    to return a corresponding message.
    
    receiving data from db-service
    
    :param consumer: an instance of a Kafka consumer using to consume messages from a Kafka topic
    :param request_id: Process the response based on the request ID provided
    :return: returns a dictionary containing a message based on the status of the response received from Kafka.     
    """
    message_count = 0
    while True:
        try:
            message = await asyncio.wait_for(consumer.getone(), timeout=5)
        
            response = json.loads(message.value.decode("utf-8"))
            status = response.get("status").get("status")

            message = "Operation failed"

            if response.get("request_id") == request_id:
                if status == "success":
                    message = "Product created successfully"
                elif status == "duplicate":
                    message = "Product already exists"
                elif status == "exist":
                    message = "Product already exists"
                elif status == "failed":
                    message = "Failed to create product"
                elif status == "not-found":
                    message = "Product not found"
                elif status == "success-update":
                    message = "Product update successfully"
                elif status == "failed-update":
                    message = "Failed to update product"
                elif status == "success-delete":
                    message = "Product deleted successfully"
                elif status == "failed-delete":
                    message = "Failed to delete product"

                return {"message": message}
        except asyncio.TimeoutError:
            return {"message": "No messages received."}

async def consume_events(topic, group_id):
    """
    This function asynchronously consumes messages from a Kafka topic, processes the
    data, and produces an inventory update after successfully generate an order and receive its payment.
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
            response = json.loads(message.value.decode("utf-8"))
            request_id = response.get("request_id")
            data = response.get("data")
            await update_product_inventory(data)
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()
        
async def get_kafka_consumer():
    consumer = AIOKafkaConsumer(
        config.KAFKA_PRODUCTS_DB_RESPONSE,
        bootstrap_servers=str(config.BOOTSTRAP_SERVER),
        group_id=config.KAFKA_PRODUCT_CONSUMER_GROUP_ID,
        auto_offset_reset="earliest",
    )
    await consumer.start()
    return consumer
