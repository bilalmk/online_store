from confluent_kafka import Consumer, KafkaError
from app import config
import os
from datetime import datetime


async def consume_events(topic):
    # Create a consumer instance.
    
    consumer = Consumer({
        'bootstrap.servers': config.BOOTSTRAP_SERVER,
        'group.id': config.KAFKA_CONSUMER_GROUP_ID,
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe([topic])
    filename = "example.txt"
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break
            
        # print(f"Received message: {msg.value().decode('utf-8')}")
        f"Received message: {msg.value.decode()} on topic {msg.topic}"
           
        content = f"{datetime.now().time()}  - Received message: {msg.value.decode()} on topic {msg.topic}"
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
