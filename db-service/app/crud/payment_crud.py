import sys

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from shared.models.payment import CreatePayment, Payment


class Payment_Crud:
    def __init__(self, session) -> None:
        self.session = session

    def create_payment(self, payment: CreatePayment):
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
            print(str(e))
            sys.stdout.flush()
            self.session.rollback()
            return {"status": False, "message": str(e)}
