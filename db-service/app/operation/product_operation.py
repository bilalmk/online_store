import json
from app.crud.product_crud import Product_Crud
from shared.models.product import CreateProduct, UpdateProduct
from app.config import get_session
from app import config
from app.kafka_producer import send_producer
import sys

"""
This class will use to handle curd operations for product data.
- The `__init__` method initializes the class with the provided data and sets the `operation` attribute

- The `operations` method is an asynchronous method that performs the following tasks:
    - It creates a database session using the `get_session` context manager.
    - Product_Crud(session)` is creating an instance of the `Product_Crud` class 
            by passing the `session` object as a parameter to its constructor. 
            This instance is then used to perform database operations like 
            creating, updating, or deleting product data in the database.
    - Based on the `operation` attribute, it calls the appropriate method:
        - If the operation is 'create', it creates a new product using the `create_product` method of the `Product_Crud` class.
        - If the operation is 'update', it updates an existing product using the `update_product` method of the `Product_Crud` class.
        - If the operation is 'delete', it deletes a product using the `delete_product` method of the `Product_Crud` class.
    - The result of the operation is stored in the `status` variable.
    - A response dictionary is created with the `request_id` and `status` data.
    - The response is converted to a JSON string and encoded as UTF-8 bytes.
    - The `send_producer` function is called asynchronously to send the response to a Kafka producer for further processing.
"""
class ProductOperation:
    def __init__(self, data):
        self.request_id = data.get("request_id")
        self.operation = data.get("operation")
        self.entity_data = data.get("data")
        self.db_data = None
        # self.operations()

    async def operations(self):
        with get_session() as session:
            if self.operation == "create":
                
                product_crud = Product_Crud(session)
                status = product_crud.create_product(CreateProduct(**self.entity_data))
                response = {"request_id": self.request_id, "status": status}
                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_PRODUCTS_DB_RESPONSE, obj)
                
            elif self.operation == "update":
                
                product_crud = Product_Crud(session)
                status = product_crud.update_product(self.entity_data, self.request_id)
                response = {"request_id": self.request_id, "status": status}
                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_PRODUCTS_DB_RESPONSE, obj)
                
            elif self.operation == "delete":
                
                product_crud = Product_Crud(session)
                status = product_crud.delete_product(self.request_id)
                response = {"request_id": self.request_id, "status": status}
                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_PRODUCTS_DB_RESPONSE, obj)