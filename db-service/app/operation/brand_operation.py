import json
from app.crud.brand_crud import Brand_Crud
from shared.models.brand import CreateBrand
from app.config import get_session
from app import config
from app.kafka_producer import send_producer
import sys

"""
This class will use to handle curd operations for brand data.
- The `__init__` method initializes the class with the provided data and sets the `operation` attribute

- The `operations` method is an asynchronous method that performs the following tasks:
    - It creates a database session using the `get_session` context manager.
    - Brand_Crud(session)` is creating an instance of the `Brand_Crud` class 
            by passing the `session` object as a parameter to its constructor. 
            This instance is then used to perform database operations like 
            creating, updating, or deleting brand data in the database.
    - Based on the `operation` attribute, it calls the appropriate method:
        - If the operation is 'create', it creates a new brand using the `create_brand` method of the `Brand_Crud` class.
        - If the operation is 'update', it updates an existing brand using the `update_brand` method of the `Brand_Crud` class.
        - If the operation is 'delete', it deletes a brand using the `delete_brand` method of the `Brand_Crud` class.
    - The result of the operation is stored in the `status` variable.
    - A response dictionary is created with the `request_id` and `status` data.
    - The response is converted to a JSON string and encoded as UTF-8 bytes.
    - The `send_producer` function is called asynchronously to send the response to a Kafka producer for further processing.
"""

class BrandOperation:
    def __init__(self, data):
        self.request_id = data.get("request_id")
        self.operation = data.get("operation")
        self.entity_data = data.get("data")
        self.db_data = None
        # self.operations()

    async def operations(self):
        with get_session() as session:
            if self.operation == "create":
                
                brand_crud = Brand_Crud(session)
                status = brand_crud.create_brand(CreateBrand(**self.entity_data))
                response = {"request_id": self.request_id, "status": status}
                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_BRAND_DB_RESPONSE, obj)
                
            elif self.operation == "update":
                
                brand_crud = Brand_Crud(session)
                status = brand_crud.update_brand(self.entity_data, self.request_id)
                response = {"request_id": self.request_id, "status": status}
                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_BRAND_DB_RESPONSE, obj)
                
            elif self.operation == "delete":
                
                brand_crud = Brand_Crud(session)
                status = brand_crud.delete_brand(self.request_id)
                response = {"request_id": self.request_id, "status": status}
                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_BRAND_DB_RESPONSE, obj)