from sqlmodel import SQLModel
class InventoryProductUpdate(SQLModel):
    product_id: int
    quantity: int