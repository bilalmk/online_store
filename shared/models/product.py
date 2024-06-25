from sqlmodel import SQLModel, Field
class Product(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    price: float