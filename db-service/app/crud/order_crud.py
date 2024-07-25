import json
import sys

from fastapi import HTTPException
from shared.models.order import CreateOrder, Order
from shared.models.order_detail import CreateOrderDetail, OrderDetail
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from shared.models.order_detail_model import CreateOrderWithDetail

"""
    A class to perform CRUD operations for orders in the database.

    Args:
        session: The database session to execute queries.

    Methods:
        create_order(order): Create a new order with details.
        get_order_by_id(id): Retrieve an order by ID.
        get_order_by_guid(id): Retrieve an order by GUID.
        get_orders(customer_id): Retrieve all orders for a specific customer.
        update_order_payment_status(id, status): Update the payment status of an order.
        update_order_notification_status(id, status): Update the notification status of an order.
"""

# The Order_Crud class provides methods to interact with the Order and OrderDetail models in the database. 
# It includes functionalities to create, retrieve, and update orders.
class Order_Crud:

    def __init__(self, session):
        # Initializes the class with a database session
        self.session = session

    # Create a new order with details.
    def create_order(self, order: CreateOrderWithDetail):
        """
        The function creates a new order in a database, handling cases where the order already exists,
        encounters integrity errors, or fails for other reasons.
        
        The method first checks if a order with the guid
        already exists in the database. If a order is found, it returns a "exist" status
        
        The possible values for the "error" key are :
        - "True": If a order with the same guid is already exists in the database.
        - "False": If the order creation process is successful.
        - "True": If there is an integrity error due to a duplicate entry.
        - "True": if an exception occurs during the operation
        """
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

            # insert parent order record
            db_order.order_status = "created"
            self.session.add(db_order)
            self.session.commit()
            self.session.refresh(db_order)

            db = db_order.dict()
            
            # insert order detail record in child table
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

    # Retrieve orders by ID
    def get_order_by_id(self, id):
        """
        This function retrieves a order from the database based on the provided order id.
        
        It queries the database to find a order with the provided id and a active status
        return the order object or None if order not found
        """
        try:
            statement = select(Order).where(Order.order_id == id).where(Order.status == 1)
            order = self.session.exec(statement).first()

            if not order:
                return None

            return order
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Retrieve orders by GUID
    def get_order_by_guid(self, id):
        """
        This function retrieves a order from the database based on the provided order guid.
        
        It queries the database to find a order with the provided guid and a active status
        return the order object or None if order not found
        """
        try:
            statement = select(Order).where(Order.guid == id).where(Order.status == 1)
            order = self.session.exec(statement).first()

            if not order:
                return None

            return order
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Retrieve all orders for a specific customer.
    def get_orders(self, customer_id):
        """
        This function retrieves orders with active status for a specific customer ID from a
        database.
        
        It queries the database to find a order for the provided customer id and a active status
        return the order object or None if order not found or raise 500 error
        """
        try:
            statement = (
                select(Order)
                .where(Order.status == 1)
                .where(Order.customer_id == customer_id)
            )
            orders = self.session.exec(statement).all()
            
            if not orders:
                return None
            
            return orders
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Update the payment status of an order
    def update_order_payment_status(self, id, status):
        """
        This function is used to updates the payment status of an order in a database.
        find the order for the provided order id return None if order is not found
        set the payment status of order and return updated order object or raise 500 error in case of exception
        """
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
    
    # Update the notification status of an order.
    def update_order_notification_status(self, id, status):
        """
        This function is used to updates the notification status of an order in a database.
        find the order for the provided order id return None if order is not found
        set the notification status of order and return updated order object or raise 500 error in case of exception
        """
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
