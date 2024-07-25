import sys

from fastapi import HTTPException
from shared.models.customer import CreateCustomer, Customer, PublicCustomer, DBCustomer, UpdateCustomer
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

"""
The Customer_Crud class provides CRUD operations for managing customers data in a database. 
It includes methods for creating, updating, deleting, and retrieving customers, 
as well as password hashing and verification.
"""

class Customer_Crud:
    # instance for password hashing
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, session):
        # Initializes the class with a database session
        self.session = session

    # Hashes a plain text password
    def get_hash_password(self, password):
        return self.pwd_context.hash(password)

    # creates a new customer in the database
    def create_customer(self, customer: CreateCustomer):
        """
        The function creates a new customer in a database, handling cases where the customer already exists,
        encounters integrity errors, or fails for other reasons.
        
        The method first checks if a customer with the same email
        already exists in the database. If a customer with the same email is found, it returns a "status"
        
        The possible values for the "status" key are:
        - "exist": If a customer with the same email already exists in the database.
        - "success": If the customer creation process is successful.
        - "duplicate": If there is an integrity error due to a duplicate entry.
        - "failed": If there is an exception occurs during the operation.
        """
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
        
    #  Updates an existing customer's information
    def update_customer(self, customer: UpdateCustomer, request_id: str):
        """
        This function updates a customer in the database based on the provided customer data and request ID.
        `request_id` is used to filter the query to find the specific customer 
        based on their `guid` and `status` in the database
        
        returns a dictionary with a status key indicating the
        outcome of the update operation. The possible status values that can be returned are:
        1. "not-found" if the customer with the provided request_id and active status is not found in the database.
        2. "success-update" if the customer is successfully updated in the database.
        3. "failed-update" if an exception occurs during the operation
        """
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

    # Soft deletes a customer by setting their status to inactive
    def delete_customer(self, request_id: str):
        """
        - This function deletes a customer by changing their status to 2 in the database (soft delete).
        - The `request_id` parameter which is a GUID of the customer that needs to be deleted from the database
        - This request_id will be used to get the customer from database
        - Returns a dictionary with a "status" key indicating the outcome of the operation. 
        - The possible return values are:
            1. "not-found if the customer with the provided request_id is not found in the database.
            2. "success-delete" if the customer is found and successfully marked as deleted (status changed to 2).
            3. "failed-delete" if an exception occurs during the operation
        """
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

    # Retrieves a customer by their email.
    def get_customer(self, email):
        """
        This function retrieves a customer from the database based on the provided email address.
        
        It queries the database to find a customer with the provided email address and a active status
        return the customer object or None if customer not found
        """
        try:
            statement = select(Customer).where(Customer.email == email).where(Customer.status == 1)
            customer = self.session.exec(statement).first()
            if not customer:
                return None
            return customer
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Retrieves a customer by their ID.
    def get_customer_by_id(self, id):
        """
        This function retrieves a customer from the database based on the provided id.
        
        It queries the database to find a customer with the provided id and a active status
        return the customer object or None if customer not found
        """
        try:
            statement = select(Customer).where(Customer.id == id).where(Customer.status == 1)
            customer = self.session.exec(statement).first()
            if not customer:
                return None
            return customer
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Verifies a plain text password against a hashed password.
    def varify_password(self, password: str, hashed_password: str):
        """
        The function takes a password and a hashed password as input, verifies if the
        password matches the hashed password stored in the database, and returns True if they match,
        otherwise None.
        """
        if not self.pwd_context.verify(password, hashed_password):
            return None
        return True

    # Retrieves all active customer.
    def get_customers(self):
        """
        This function retrieves all customers with active status from the database and return this list in response.
        """
        try:
            statement = select(Customer).where(Customer.status == 1)
            customers = self.session.exec(statement).all()
            return customers
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
