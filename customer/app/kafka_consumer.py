import json
import sys
from aiokafka import AIOKafkaConsumer
from fastapi import HTTPException  # type: ignore
from app import config
import os
from datetime import datetime

responses = {}

async def consume_response_from_kafka(consumer, request_id):
    """
    The function consumes messages from a Kafka consumer and processes the response based on the status
    to return a corresponding message.
    
    receiving data from db-service
    
    :param consumer: an instance of a Kafka consumer using to consume messages from a Kafka topic
    :param request_id: Process the response based on the request ID provided
    :return: returns a dictionary containing a message based on the status of the response received from Kafka.     
    """
    # count=0
    async for msg in consumer:
        # if(count>50):
        #    break
        # count = count+1
        response = json.loads(msg.value.decode("utf-8"))
        status = response.get("status").get("status")

        message = "Operation failed"
        
        if response.get("request_id") == request_id:
            if status == "success":
                message = "Customer created successfully"
            elif status == "duplicate":
                message = "Record already exists"
            elif status == "exist":
                message = "Customer already exists"
            elif status == "failed":
                message = "Failed to create Customer"
            elif status == "not-found":
                message = "Customer not found"
            elif status == "success-update":
                message = "Customer update successfully"
            elif status == "failed-update":
                message = "Failed to update customer"
            elif status == "success-delete":
                message = "Customer deleted successfully"
            elif status == "failed-delete":
                message = "Failed to delete customer"

            return {"message": message}
        # raise HTTPException(status_code=500, detail="No response from db-service")


"""create and return kafka consumer"""
async def get_kafka_consumer():
    consumer = AIOKafkaConsumer(
        config.KAFKA_CUSTOMER_DB_RESPONSE,
        bootstrap_servers=str(config.BOOTSTRAP_SERVER),
        group_id=config.KAFKA_CUSTOMER_CONSUMER_GROUP_ID,
        auto_offset_reset="earliest",
    )
    await consumer.start()
    return consumer


# def log_message(entity_data, topic):
#     # print(f"Received message: {message.value.decode()} on topic {message.topic}")
#     # content = f"{datetime.now().time()}  - Received message: {entity_data} on topic {message.topic} and dbuser is {db_user}"

#     filename = "example.txt"
#     content = (
#         f"{datetime.now().time()}  - Received message: {entity_data} on topic {topic}"
#     )
#     write_to_file(filename, content)

# def write_to_file(filename, content):
#     # Check if the file exists
#     if os.path.exists(filename):
#         # Open the file in append mode
#         with open(filename, "a") as file:
#             file.write(content + "\n")
#     else:
#         # Create a new file and write to it
#         with open(filename, "w") as file:
#             file.write(content + "\n")
