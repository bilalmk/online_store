import os
from dotenv import load_dotenv
load_dotenv()

BOOTSTRAP_SERVER = os.environ.get("BOOTSTRAP_SERVER")
KAFKA_ORDER_TOPIC = os.environ.get("KAFKA_ORDER_TOPIC")
KAFKA_CONSUMER_GROUP_ID = os.environ.get("KAFKA_CONSUMER_GROUP_ID")
