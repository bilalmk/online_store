import sys

from fastapi import HTTPException
from shared.models.user import CreateUser, User, PublicUser, DBUser, UpdateUser
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

    def update_hero(self, user: UpdateUser, request_id: str):
        try:
            db_user = self.session.query(User).filter(User.guid == request_id).first()
            if not db_user:
                return {"status": "not-found"}
            
            db_user.sqlmodel_update(user)
            self.session.add(db_user)
            self.session.commit()
            self.session.refresh(db_user)
            return {"status": "success-update"}
        except Exception as e:
            print(str(e))
            sys.stdout.flush()
            self.session.rollback()
            return {"status": "failed-update"}        

    def get_user(self, email):
        try:
            statement = select(User).where(User.email == email).where(User.status == 1)
            user = self.session.exec(statement).first()
            if not user:
                return None
            return user
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_user_by_id(self, id):
        try:
            statement = select(User).where(User.id == id).where(User.status == 1)
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

    def get_users(self):
        try:
            statement = select(User).where(User.status == 1)
            users = self.session.exec(statement).all()
            return users
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
