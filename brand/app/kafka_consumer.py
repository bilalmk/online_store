import json
import asyncio
from aiokafka import AIOKafkaConsumer  # type: ignore
from app import config

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
                    message = "Brand created successfully"
                elif status == "duplicate":
                    message = "Brand already exists"
                elif status == "exist":
                    message = "Brand already exists"
                elif status == "failed":
                    message = "Failed to create brand"
                elif status == "not-found":
                    message = "Brand not found"
                elif status == "success-update":
                    message = "Brand update successfully"
                elif status == "failed-update":
                    message = "Failed to update brand"
                elif status == "success-delete":
                    message = "Brand deleted successfully"
                elif status == "failed-delete":
                    message = "Failed to delete brand"

                return {"message": message}
        except asyncio.TimeoutError:
            return {"message": "No messages received."}


async def get_kafka_consumer():
    consumer = AIOKafkaConsumer(
        config.KAFKA_BRAND_DB_RESPONSE,
        bootstrap_servers=str(config.BOOTSTRAP_SERVER),
        group_id=config.KAFKA_BRAND_CONSUMER_GROUP_ID,
        auto_offset_reset="earliest",
    )
    await consumer.start()
    return consumer
