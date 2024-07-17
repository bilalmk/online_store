from shared.models.order import PublicOrder
from app.config import sessionDep
from app.crud.order_crud import Order_Crud
from fastapi import Depends, HTTPException, APIRouter, Form
from fastapi import APIRouter

from shared.models.order_detail_model import PublicOrderWithDetail

def get_order_crud(session: sessionDep) -> Order_Crud:
    return Order_Crud(session)

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)

@router.post("/order", response_model=PublicOrderWithDetail)
async def get_order(order_id: str = Form(...), order_crud=Depends(get_order_crud)):
    order = order_crud.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order

@router.get("/", response_model=list[PublicOrder])
async def get_orders(order_crud=Depends(get_order_crud)):
    orders = order_crud.get_orders()
    if not orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders