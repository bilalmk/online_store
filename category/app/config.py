import os
from dotenv import load_dotenv

load_dotenv()

BOOTSTRAP_SERVER = os.environ.get("BOOTSTRAP_SERVER")
KAFKA_CATEGORY_TOPIC = os.environ.get("KAFKA_CATEGORY_TOPIC")
KAFKA_CATEGORY_CONSUMER_GROUP_ID = os.environ.get("KAFKA_CATEGORY_CONSUMER_GROUP_ID")
KAFKA_CATEGORY_DB_RESPONSE = os.environ.get("KAFKA_CATEGORY_DB_RESPONSE")
AUTH_API_BASE_PATH = os.environ.get("AUTH_API_BASE_PATH")
DB_API_BASE_PATH = os.environ.get("DB_API_BASE_PATH")
client_session = None
