import json
import sys

from fastapi import HTTPException
from shared.models.order import CreateOrder, Order
from shared.models.order_detail import CreateOrderDetail, OrderDetail
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from shared.models.order_detail_model import CreateOrderWithDetail


class Order_Crud:

    def __init__(self, session):
        self.session = session

    def create_order(self, order: CreateOrderWithDetail):
        try:
            statement = select(Order).where(Order.guid == order.guid)
            result = self.session.exec(statement).first()

            if result:
                return {"error": True, "status": "exist"}

            # db_order = CreateOrderWithDetail.model_validate(order)

            db_order = Order(
                customer_id=order.customer_id,
                total_amount=order.total_amount,
                order_date=order.order_date,
                shipping_address=order.shipping_address,
                billing_address=order.billing_address,
                payment_method=order.payment_method,
                payment_status=order.payment_status,
                delivery_date=order.delivery_date,
                delivery_status=order.delivery_status,
                order_status=order.order_status,
                guid=order.guid,
                created_at=order.created_at,
                status=order.status,
            )

            db_order = Order.model_validate(db_order)

            db_order.order_status = "created"
            self.session.add(db_order)
            self.session.commit()
            self.session.refresh(db_order)

            db = db_order.dict()
            for details in order.order_details:
                details.order_id = db_order.order_id
                db_detail = OrderDetail.model_validate(details)
                self.session.add(db_detail)
                self.session.commit()
                self.session.refresh(db_detail)

            return {"error": False, "status": "success", "order": db}
        except IntegrityError:
            self.session.rollback()
            return {"error": True, "status": "duplicate"}
        except Exception as e:
            print("crud error")
            print("=====================")
            print(str(e))
            sys.stdout.flush()
            self.session.rollback()
            return {"error": True, "status": "failed"}

    def get_order_by_id(self, id):
        try:
            statement = select(Order).where(Order.order_id == id).where(Order.status == 1)
            order = self.session.exec(statement).first()

            if not order:
                return None

            return order
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    def get_order_by_guid(self, id):
        try:
            statement = select(Order).where(Order.guid == id).where(Order.status == 1)
            order = self.session.exec(statement).first()

            if not order:
                return None

            return order
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_orders(self, customer_id):
        try:
            statement = (
                select(Order)
                .where(Order.status == 1)
                .where(Order.customer_id == customer_id)
            )
            orders = self.session.exec(statement).all()
            return orders
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    def update_order_payment_status(self, id, status):
        try:
            statement = select(Order).where(Order.order_id == id).where(Order.status == 1)
            order = self.session.exec(statement).first()
            
            if not order:
                return None

            order.payment_status = status
            self.session.add(order)
            self.session.commit()
            self.session.refresh(order)
            
            return order
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    def update_order_notification_status(self, id, status):
        try:
            statement = select(Order).where(Order.order_id == id).where(Order.status == 1)
            order = self.session.exec(statement).first()
            
            if not order:
                return None

            order.notification_status = int(status)
            self.session.add(order)
            self.session.commit()
            self.session.refresh(order)
            
            return order
        except Exception as e:
            print(str(e))
            sys.stdout.flush()
            raise HTTPException(status_code=500, detail=str(e))

    # def update_product(self, product: UpdateProduct, request_id: str):
    #     try:
    #         db_product: Product = (
    #             self.session.query(Product)
    #             .filter(Product.guid == request_id)
    #             .filter(Product.status == 1)
    #             .first()
    #         )

    #         if not db_product:
    #             return {"status": "not-found"}

    #         db_product.sqlmodel_update(product)
    #         self.session.add(db_product)
    #         self.session.commit()
    #         self.session.refresh(db_product)
    #         return {"status": "success-update"}
    #     except Exception as e:
    #         self.session.rollback()
    #         return {"status": "failed-update"}

    # def delete_product(self, request_id: str):
    #     try:

    #         statement = (
    #             select(Product).where(Product.guid == request_id).where(Product.status == 1)
    #         )
    #         db_product = self.session.exec(statement).first()

    #         if not db_product:
    #             return {"status": "not-found"}

    #         db_product.status = 2
    #         self.session.commit()
    #         return {"status": "success-delete"}

    #     except Exception as e:
    #         self.session.rollback()
    #         return {"status": "failed-delete"}

    # def get_product(self, id):
    #     try:
    #         statement = select(Product).where(Product.id == id).where(Product.status == 1)
    #         product = self.session.exec(statement).first()
    #         if not product:
    #             return None
    #         return product
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=str(e))
