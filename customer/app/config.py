import os
from dotenv import load_dotenv

load_dotenv()

BOOTSTRAP_SERVER = os.environ.get("BOOTSTRAP_SERVER")
KAFKA_CUSTOMER_TOPIC = os.environ.get("KAFKA_CUSTOMER_TOPIC")
KAFKA_CUSTOMER_CONSUMER_GROUP_ID = os.environ.get("KAFKA_CUSTOMER_CONSUMER_GROUP_ID")
KAFKA_CUSTOMER_DB_RESPONSE = os.environ.get("KAFKA_CUSTOMER_DB_RESPONSE")
AUTH_API_BASE_PATH = os.environ.get("AUTH_API_BASE_PATH")
DB_API_BASE_PATH = os.environ.get("DB_API_BASE_PATH")
client_session = None
