import json
from app.crud.brand_crud import Brand_Crud
from shared.models.brand import CreateBrand
from app.config import get_session
from app import config
from app.kafka_producer import send_producer
import sys


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