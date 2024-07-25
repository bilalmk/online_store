import json
from app.crud.user_crud import User_Crud
from shared.models.user import CreateUser, UpdateUser
from app.config import get_session
from app import config
from app.kafka_producer import send_producer
import sys


"""
This class will use to handle curd operations for user data.
- The `__init__` method initializes the class with the provided data and sets the `operation` attribute

- The `operations` method is an asynchronous method that performs the following tasks:
    - It creates a database session using the `get_session` context manager.
    - User_Crud(session)` is creating an instance of the `User_Crud` class 
            by passing the `session` object as a parameter to its constructor. 
            This instance is then used to perform database operations like 
            creating, updating, or deleting user data in the database.
    - Based on the `operation` attribute, it calls the appropriate method:
        - If the operation is 'create', it creates a new user using the `create_user` method of the `User_Crud` class.
        - If the operation is 'update', it updates an existing user using the `update_user` method of the `User_Crud` class.
        - If the operation is 'delete', it deletes a user using the `delete_user` method of the `User_Crud` class.
    - The result of the operation is stored in the `status` variable.
    - A response dictionary is created with the `request_id` and `status` data.
    - The response is converted to a JSON string and encoded as UTF-8 bytes.
    - The `send_producer` function is called asynchronously to send the response to a Kafka producer for further processing.
"""

class UserOperation:
    def __init__(self, data):
        self.request_id = data.get("request_id")
        self.operation = data.get("operation")
        self.entity_data = data.get("data")
        self.db_data = None
        # self.operations()

    async def operations(self):
        with get_session() as session:
            if self.operation == "create":
                user_crud = User_Crud(session)
                status = user_crud.create_user(CreateUser(**self.entity_data))
                response = {"request_id": self.request_id, "status": status}
                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_USER_DB_RESPONSE, obj)
                
            elif self.operation == "update":
                
                user_crud = User_Crud(session)
                status = user_crud.update_user(self.entity_data, self.request_id)
                response = {"request_id": self.request_id, "status": status}
                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_USER_DB_RESPONSE, obj)
                
            elif self.operation == "delete":
                
                user_crud = User_Crud(session)
                status = user_crud.delete_user(self.request_id)
                response = {"request_id": self.request_id, "status": status}
                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_USER_DB_RESPONSE, obj)