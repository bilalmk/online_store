import sys

from fastapi import HTTPException
from shared.models.user import CreateUser, User, PublicUser, DBUser, UpdateUser
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

"""
The User_Crud class provides CRUD operations for managing user data in a database. 
It includes methods for creating, updating, deleting, and retrieving users, 
as well as password hashing and verification.
"""
class User_Crud:
    # instance for password hashing
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, session):
        # Initializes the class with a database session
        self.session = session

    # Hashes a plain text password
    def get_hash_password(self, password):
        return self.pwd_context.hash(password)

    # creates a new user in the database
    def create_user(self, user: CreateUser):
        """
        The function creates a new user in a database, handling cases where the user already exists,
        encounters integrity errors, or fails for other reasons.
        
        The method first checks if a user with the same email
        already exists in the database. If a user with the same email is found, it returns a "status"
        
        The possible values for the "status" key are:
        - "exist": If a user with the same email already exists in the database.
        - "success": If the user creation process is successful.
        - "duplicate": If there is an integrity error due to a duplicate entry.
        - "failed": if an exception occurs during the operation
        """
        try:
            statement = select(User).where(User.email == user.email)
            result = self.session.exec(statement).first()
            if result:
                return {"status": "exist"}

            user.password = self.get_hash_password(user.password)
            # db_user = User(**user.dict(exclude={"password"}))
            db_user = User.model_validate(user)
            self.session.add(db_user)
            self.session.commit()
            self.session.refresh(db_user)
            return {"status": "success"}
        except IntegrityError:
            self.session.rollback()
            return {"status": "duplicate"}
        except Exception as e:
            print(str(e))
            sys.stdout.flush()
            self.session.rollback()
            return {"status": "failed"}

    #  Updates an existing user's information
    def update_user(self, user: UpdateUser, request_id: str):
        """
        This function updates a user in the database based on the provided user data and request ID.
        `request_id` is used to filter the query to find the specific user 
        based on their `guid` and `status` in the database
        
        returns a dictionary with a status key indicating the
        outcome of the update operation. The possible status values that can be returned are:
        1. "not-found" if the user with the provided request_id and active status is not found in the database.
        2. "success-update" if the user is successfully updated in the database.
        3. "failed-update" if an exception occurs during the operation
        """
        try:
            db_user: User = (
                self.session.query(User)
                .filter(User.guid == request_id)
                .filter(User.status == 1)
                .first()
            )

            if not db_user:
                return {"status": "not-found"}

            password = user.get("password")

            if password:
                user["password"] = self.get_hash_password(password)

            db_user.sqlmodel_update(user)
            self.session.add(db_user)
            self.session.commit()
            self.session.refresh(db_user)
            return {"status": "success-update"}
        except Exception as e:
            self.session.rollback()
            return {"status": "failed-update"}

    # Soft deletes a user by setting their status to inactive
    def delete_user(self, request_id: str):
        """
        - This function deletes a user by changing their status to 2 in the database (soft delete).
        - The `request_id` parameter which is a GUID of the user that needs to be deleted from the database
        - This request_id will be used to get the user from database
        - Returns a dictionary with a "status" key indicating the outcome of the operation. 
        - The possible return values are:
            1. "not-found if the user with the provided request_id is not found in the database.
            2. "success-delete" if the user is found and successfully marked as deleted (status changed to 2).
            3. "failed-delete" if an exception occurs during the operation
        """
        try:

            statement = (
                select(User).where(User.guid == request_id).where(User.status == 1)
            )
            db_user = self.session.exec(statement).first()

            if not db_user:
                return {"status": "not-found"}

            # self.session.delete(hero)
            db_user.status = 2
            self.session.commit()
            return {"status": "success-delete"}

        except Exception as e:
            self.session.rollback()
            return {"status": "failed-delete"}

    # Retrieves a user by their email.
    def get_user(self, email):
        """
        This function retrieves a user from the database based on the provided email address.
        
        It queries the database to find a user with the provided email address and a active status
        return the user object or None if user not found
        """
        try:
            statement = select(User).where(User.email == email).where(User.status == 1)
            user = self.session.exec(statement).first()
            if not user:
                return None
            return user
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Retrieves a user by their ID.
    def get_user_by_id(self, id):
        """
        This function retrieves a user from the database based on the provided id.
        
        It queries the database to find a user with the provided id and a active status
        return the user object or None if user not found
        """
        try:
            statement = select(User).where(User.id == id).where(User.status == 1)
            user = self.session.exec(statement).first()
            if not user:
                return None
            return user
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

    # Retrieves all active users.
    def get_users(self):
        """
        This function retrieves all users with active status from the database and return this list in response.
        """
        try:
            statement = select(User).where(User.status == 1)
            users = self.session.exec(statement).all()
            return users
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
