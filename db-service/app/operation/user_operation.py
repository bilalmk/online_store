import json
from app.crud.user_crud import User_Crud
from shared.models.user import CreateUser
from app.config import get_session
from app import config
from app.kafka_producer import send_producer


class UserOperation:
    def __init__(self, data):
        self.request_id = data.get("request_id")
        self.operation = data.get("operation")
        self.entity_data = data.get("data")
        self.db_data = None
        # self.operations()

    async def operations(self):
        with get_session() as session:
            if self.operation == "create":
                hero_crud = User_Crud(session)
                status = hero_crud.create_user(CreateUser(**self.entity_data))
                response = {"uuid": self.request_id, "status": status}
                obj = json.dumps(response).encode("utf-8")
                await send_producer(config.KAFKA_USER_DB_RESPONSE, obj)
            elif self.operation == "update":
                print(f"Updating user: {self.entity_data}")
            elif self.operation == "delete":
                print(f"Deleting user: {self.entity_data}")
