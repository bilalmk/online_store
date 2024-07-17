from typing import Optional
from shared.models.order import CreateOrder, PublicOrder
from shared.models.order_detail import CreateOrderDetail, PublicOrderDetail


class PublicOrderWithDetail(PublicOrder):
    order_details: list["PublicOrderDetail"] = [] 

class CreateOrderWithDetail(CreateOrder):
    order_details: list["CreateOrderDetail"] = []