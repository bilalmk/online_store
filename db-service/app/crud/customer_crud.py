import sys

from fastapi import HTTPException
from shared.models.customer import CreateCustomer, Customer, PublicCustomer, DBCustomer, UpdateCustomer
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlmodel import select


class Customer_Crud:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, session):
        self.session = session

    def get_hash_password(self, password):
        return self.pwd_context.hash(password)

    def create_customer(self, customer: CreateCustomer):
        try:
            statement = select(Customer).where(Customer.email == customer.email)
            result = self.session.exec(statement).first()
            if result:
                return {"status": "exist"}

            customer.password = self.get_hash_password(customer.password)
            # db_customer = customer(**customer.dict(exclude={"password"}))
            db_customer = Customer.model_validate(customer)
            self.session.add(db_customer)
            self.session.commit()
            self.session.refresh(db_customer)
            return {"status": "success"}
        except IntegrityError:
            self.session.rollback()
            return {"status": "duplicate"}
        except Exception as e:
            print(str(e))
            sys.stdout.flush()
            self.session.rollback()
            return {"status": "failed"}

    def update_customer(self, customer: UpdateCustomer, request_id: str):
        try:
            db_customer: Customer = (
                self.session.query(Customer)
                .filter(Customer.guid == request_id)
                .filter(Customer.status == 1)
                .first()
            )

            if not db_customer:
                return {"status": "not-found"}
            
            password = customer.get("password")
            
            if password:
                customer["password"] = self.get_hash_password(password)
        
            db_customer.sqlmodel_update(customer)
            self.session.add(db_customer)
            self.session.commit()
            self.session.refresh(db_customer)
            return {"status": "success-update"}
        except Exception as e:
            self.session.rollback()
            return {"status": "failed-update"}

    def delete_hero(self, request_id: str):
        try:

            statement = (
                select(Customer).where(Customer.guid == request_id).where(Customer.status == 1)
            )
            db_customer = self.session.exec(statement).first()

            if not db_customer:
                return {"status": "not-found"}

            # self.session.delete(hero)
            db_customer.status = 2
            self.session.commit()
            return {"status": "success-delete"}

        except Exception as e:
            self.session.rollback()
            return {"status": "failed-delete"}

    def get_customer(self, email):
        try:
            statement = select(Customer).where(Customer.email == email).where(Customer.status == 1)
            customer = self.session.exec(statement).first()
            if not customer:
                return None
            return customer
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_customer_by_id(self, id):
        try:
            statement = select(Customer).where(Customer.id == id).where(Customer.status == 1)
            customer = self.session.exec(statement).first()
            if not customer:
                return None
            return customer
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def varify_password(self, password: str, hashed_password: str):
        if not self.pwd_context.verify(password, hashed_password):
            return None
        return True

    def get_customers(self):
        try:
            statement = select(Customer).where(Customer.status == 1)
            customers = self.session.exec(statement).all()
            return customers
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
