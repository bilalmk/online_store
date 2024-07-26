from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from shared.models.payment import CreatePayment, Payment

"""
This code defines a Payment_Crud class with methods to interact with a database session for creating payments. 
It includes error handling for integrity errors and general exceptions.
"""
class Payment_Crud:
    def __init__(self, session) -> None:
        # Initializes the class with a database session
        self.session = session

    # Attempts to create a new payment record in the database, handling integrity errors and other exceptions.
    def create_payment(self, payment: CreatePayment):
        """
        The function creates a new payment in a database, handling cases where the payment already exists,
        encounters integrity errors, or fails for other reasons.
        
        The method first checks if a payment with the guid
        already exists in the database. If a payment is found, it returns a "exist" status
        
        The possible values for the "status" key are:
        - "False": If a payment with the same order_id and customer_id is already exists in the database.
        - "True": If the payment creation process is successful.
        - "False": If there is an integrity error due to a duplicate entry.
        - "False": if an exception occurs during the operation
        """
        try:
            statement = (
                select(Payment)
                .where(Payment.order_id == payment.order_id)
                .where(Payment.customer_id == payment.customer_id)
            )
            result = self.session.exec(statement).first()
            
            if result:
                return {"status": False, "message": "Payment already exists"}
            
            payment_db = Payment.model_validate(payment)
            self.session.add(payment_db)
            self.session.commit()
            self.session.refresh(payment_db)
            # return payment_db
            return {"status": True, "message": "success"}
        except IntegrityError:
            self.session.rollback()
            return {"status": False, "message": "duplicate Payment"}
        except Exception as e:
            self.session.rollback()
            return {"status": False, "message": str(e)}
