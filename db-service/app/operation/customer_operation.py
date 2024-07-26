import json
from app.crud.customer_crud import Customer_Crud
from shared.models.customer import CreateCustomer, UpdateCustomer
from app.config import get_session
from app import config
from app.kafka_producer import send_producer

"""
This class will use to handle curd operations for customer data.
- The `__init__` method initializes the class with the provided data and sets the `operation` attribute

- The `operations` method is an asynchronous method that performs the following tasks:
    - It creates a database session using the `get_session` context manager.
    - Customer_Crud(session)` is creating an instance of the `Customer_Crud` class 
            by passing the `session` object as a parameter to its constructor. 
            This instance is then used to perform database operations like 
            creating, updating, or deleting customer data in the database.
    - Based on the `operation` attribute, it calls the appropriate method:
        - If the operation is 'create', it creates a new customer using the `create_customer` method of the `Customer_Crud` class.
        - If the operation is 'update', it updates an existing customer using the `update_customer` method of the `Customer_Crud` class.
        - If the operation is 'delete', it deletes a customer using the `delete_customer` method of the `Customer_Crud` class.
    - The result of the operation is stored in the `status` variable.
    - A response dictionary is created with the `request_id` and `status` data.
    - The response is converted to a JSON string and encoded as UTF-8 bytes.
    - The `send_producer` function is called asynchronously to send the response to a Kafka producer for further processing.
"""

class CustomerOperation:
    def __init__(self, data):
        self.request_id = data.get("request_id")
        self.operation = data.get("operation")
        self.entity_data = data.get("data")
        self.db_data = None

    async def operations(self):
        with get_session() as session:
            if self.operation == "create":
                
                customer_crud = Customer_Crud(session)
                status = customer_crud.create_customer(CreateCustomer(**self.entity_data))
                response = {"request_id": self.request_id, "status": status}
                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_CUSTOMER_DB_RESPONSE, obj)
                
            elif self.operation == "update":
                
                customer_crud = Customer_Crud(session)
                status = customer_crud.update_customer(self.entity_data, self.request_id)
                response = {"request_id": self.request_id, "status": status}
                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_CUSTOMER_DB_RESPONSE, obj)
                
            elif self.operation == "delete":
                
                customer_crud = Customer_Crud(session)
                status = customer_crud.delete_customer(self.request_id)
                response = {"request_id": self.request_id, "status": status}
                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_CUSTOMER_DB_RESPONSE, obj)