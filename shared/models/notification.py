from shared.models.order_detail_model import PublicOrderWithDetail
from shared.models.user import User
from sqlmodel import Field, SQLModel


class CreateNotification(SQLModel):
    client_information: User
    order_information: PublicOrderWithDetail
