from shared.models.user import CreateUser, User
from passlib.context import CryptContext

class User_Crud:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, session):
        self.session = session

    def get_hash_password(self, password):
        return self.pwd_context.hash(password)
    
    def create_user(self, user:CreateUser):
        user.password = self.get_hash_password(user.password)
        #db_user = User(**user.dict(exclude={"password"}))
        db_user = User.model_validate(user)
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user