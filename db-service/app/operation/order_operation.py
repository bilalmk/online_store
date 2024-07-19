import datetime
from decimal import Decimal
import json
from app.crud.order_crud import Order_Crud
from shared.models.order import CreateOrder
from app.config import get_session
from app import config
from app.kafka_producer import send_producer
import sys

from shared.models.order_detail_model import CreateOrderWithDetail


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super(CustomJSONEncoder, self).default(obj)


class OrderOperation:
    def __init__(self, data):
        self.request_id = data.get("request_id")
        self.operation = data.get("operation")
        self.entity_data = data.get("data")
        self.db_data = None
        # self.operations()

    async def operations(self):
        with get_session() as session:
            if self.operation == "create":
                order_crud = Order_Crud(session)
                res = order_crud.create_order(CreateOrderWithDetail(**self.entity_data))

                error = res.get("error")
                status = res.get("status")

                try:
                    if error:
                        response = {
                            "request_id": self.request_id,
                            "status": status,
                            "order": {},
                        }
                    else:
                        self.entity_data["order_id"] = res.get("order")["order_id"]
                        self.entity_data["order_status"] = res.get("order")[
                            "order_status"
                        ]
                        order_response = self.entity_data
                        order_response.pop("order_details")

                        response = {
                            "request_id": self.request_id,
                            "status": status,
                            "order": order_response,
                        }
                except Exception as ex:
                    print("operation error")
                    print("======================")
                    print(str(ex))
                    sys.stdout.flush()
                    response = {
                        "request_id": self.request_id,
                        "status": status,
                        "order": {},
                    }

                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_ORDERS_DB_RESPONSE, obj)

            # elif self.operation == "update":

            #     product_crud = Product_Crud(session)
            #     status = product_crud.update_product(self.entity_data, self.request_id)
            #     response = {"request_id": self.request_id, "status": status}
            #     obj = json.dumps(response).encode("utf-8")
            #     await send_producer(config.KAFKA_PRODUCTS_DB_RESPONSE, obj)

            # elif self.operation == "delete":

            #     product_crud = Product_Crud(session)
            #     status = product_crud.delete_product(self.request_id)
            #     response = {"request_id": self.request_id, "status": status}
            #     obj = json.dumps(response).encode("utf-8")
            #     await send_producer(config.KAFKA_PRODUCTS_DB_RESPONSE, obj)
