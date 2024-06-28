from app.crud.user_crud import User_Crud
from shared.models.user import CreateUser
from app.config import get_session

class UserOperation:
    def __init__(self, data):
        self.operation = data.get("operation")
        self.entity_data = data.get("data")
        self.db_data = None
        self.operations()
        
    def operations(self):
        with get_session() as session:
            if self.operation == 'create':
                hero_crud = User_Crud(session)
                hero_crud.create_user(CreateUser(**self.entity_data))
            elif self.operation == 'update':
                print(f"Updating user: {self.entity_data}")
            elif self.operation == 'delete':
                print(f"Deleting user: {self.entity_data}")