import sys

from fastapi import HTTPException
from shared.models.user import CreateUser, User, PublicUser, DBUser
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlmodel import select


class User_Crud:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, session):
        self.session = session

    def get_hash_password(self, password):
        return self.pwd_context.hash(password)

    def create_user(self, user: CreateUser):
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

    def get_user(self, email):
        try:
            statement = select(User).where(User.email == email)
            user = self.session.exec(statement).first()
            if not user:
                return None
            return user
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def varify_password(self, password: str, hashed_password: str):
        if not self.pwd_context.verify(password, hashed_password):
            return None
        return True
