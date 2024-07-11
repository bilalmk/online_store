import json
from app.crud.category_crud import Category_Crud
from shared.models.category import CreateCategory
from app.config import get_session
from app import config
from app.kafka_producer import send_producer
import sys


class CategoryOperation:
    def __init__(self, data):
        self.request_id = data.get("request_id")
        self.operation = data.get("operation")
        self.entity_data = data.get("data")
        self.db_data = None
        # self.operations()

    async def operations(self):
        with get_session() as session:
            if self.operation == "create":
                
                category_crud = Category_Crud(session)
                status = category_crud.create_category(CreateCategory(**self.entity_data))
                response = {"request_id": self.request_id, "status": status}
                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_CATEGORY_DB_RESPONSE, obj)
                
            elif self.operation == "update":
                
                category_crud = Category_Crud(session)
                status = category_crud.update_category(self.entity_data, self.request_id)
                response = {"request_id": self.request_id, "status": status}
                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_CATEGORY_DB_RESPONSE, obj)
                
            elif self.operation == "delete":
                
                category_crud = Category_Crud(session)
                status = category_crud.delete_category(self.request_id)
                response = {"request_id": self.request_id, "status": status}
                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_CATEGORY_DB_RESPONSE, obj)