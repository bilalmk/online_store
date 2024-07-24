import json
from app.crud.customer_crud import Customer_Crud
from shared.models.customer import CreateCustomer, UpdateCustomer
from app.config import get_session
from app import config
from app.kafka_producer import send_producer
import sys


class CustomerOperation:
    def __init__(self, data):
        self.request_id = data.get("request_id")
        self.operation = data.get("operation")
        self.entity_data = data.get("data")
        self.db_data = None
        # self.operations()

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
                status = customer_crud.delete_hero(self.request_id)
                response = {"request_id": self.request_id, "status": status}
                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_CUSTOMER_DB_RESPONSE, obj)