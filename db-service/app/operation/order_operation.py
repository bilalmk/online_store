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


# class CustomJSONEncoder(json.JSONEncoder):
#     """ 
#     CustomJSONEncoder is a custom JSON encoder class that extends the default JSON encoder
#     from the Python standard library. It is used to handle special cases when encoding
#     objects like Decimal and datetime.
#     """
#     def default(self, obj):
#         if isinstance(obj, Decimal):
#             return float(obj)
#         elif isinstance(obj, datetime):
#             return obj.isoformat()
#         return super(CustomJSONEncoder, self).default(obj)

"""
This class will use to handle curd operations for order data.
- The `__init__` method initializes the class with the provided data and sets the `operation` attribute

- The `operations` method is an asynchronous method that performs the following tasks:
    - It creates a database session using the `get_session` context manager.
    - Order_Crud(session)` is creating an instance of the `Order_Crud` class 
            by passing the `session` object as a parameter to its constructor. 
            This instance is then used to perform database operations like 
            creating, updating, or deleting order data in the database.
    - Based on the `operation` attribute, it calls the appropriate method:
        - If the operation is 'create', it creates a new order using the `create_order` method of the `Order_Crud` class.        
    - The result of the operation is stored in the `res` variable.
    - A response dictionary is created with the:
        - `request_id`: The ID of the request.
        - `status`: The status of the operation.
        - `order`: The order data without order detail.
    - The response is converted to a JSON string and encoded as UTF-8 bytes.
    - The `send_producer` function is called asynchronously to send the response to a Kafka producer for further processing.
"""

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
