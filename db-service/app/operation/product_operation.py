import json
from app.crud.product_crud import Product_Crud
from shared.models.product import CreateProduct, UpdateProduct
from app.config import get_session
from app import config
from app.kafka_producer import send_producer
import sys


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
                status = product_crud.delete_hero(self.request_id)
                response = {"request_id": self.request_id, "status": status}
                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_PRODUCTS_DB_RESPONSE, obj)