import sys
from shared.models.order import PublicOrder
from app.config import sessionDep
from app.crud.order_crud import Order_Crud
from fastapi import Depends, HTTPException, APIRouter, Form

from shared.models.order_detail_model import PublicOrderWithDetail


def get_order_crud(session: sessionDep) -> Order_Crud:
    return Order_Crud(session)


router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)

"""
End-Point retrieves an order by its GUID:str, using a order_crud class dependency
and returns order with additional details in a response model. Raising a 404 error if no order are found

order_crud class is a dependency that is used to interact with order data in the database.
it contains methods for retrieving order information
"""
@router.post("/order_by_guid", response_model=PublicOrderWithDetail)
async def get_order_by_guid(
    order_id: str = Form(...), order_crud=Depends(get_order_crud)
):
    order = order_crud.get_order_by_guid(order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


"""
End-Point retrieves an order by its id:int, using a order_crud class dependency
and returns order with additional details in a response model. Raising a 404 error if no order are found

order_crud class is a dependency that is used to interact with order data in the database.
it contains methods for retrieving order information
"""
@router.post("/order_by_id", response_model=PublicOrderWithDetail)
async def get_order_by_id(
    order_id: int = Form(...), order_crud=Depends(get_order_crud)
):
    order = order_crud.get_order_by_id(order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


"""
End-Point retrieves an order by customer_id:int, using a order_crud class dependency
and returns order with additional details in a response model. Raising a 404 error if order not found

order_crud class is a dependency that is used to interact with order data in the database.
it contains methods for retrieving order information

This end-point is used by customer to view their orders
"""
@router.post("/customer_order", response_model=list[PublicOrderWithDetail])
async def get_orders(customer_id: int = Form(...), order_crud=Depends(get_order_crud)):
    orders = order_crud.get_orders(customer_id)

    if not orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders


"""
End-Point updates the payment status of an order using a order_crud class dependency
and returns the updated order details. Raising a 404 error if order not found

order_crud class is a dependency that is used to interact with order data in the database.
it contains methods for crud order information

This end-point is used by payment microservice to update the order payment status, after successful payment
"""
@router.patch("/update_order_payment_status", response_model=PublicOrder)
async def update_order_status(
    order_id: int = Form(...),
    payment_status: str = Form(...),
    order_crud=Depends(get_order_crud),
):
    order = order_crud.update_order_payment_status(order_id, payment_status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order

"""
End-Point updates the notification status of an order using a order_crud class dependency
and returns the updated order details. Raising a 404 error if order not found

order_crud class is a dependency that is used to interact with order data in the database.
it contains methods for crud order information

This end-point is used by notification microservice to update the order payment status, 
after successful sent notification to user about the order and payment received 
"""
@router.patch("/update_order_notification_status", response_model=PublicOrder)
async def update_order_notification_status(
    order_id: int = Form(...),
    notification_status: int = Form(...),
    order_crud=Depends(get_order_crud),
):
    try:
        order = order_crud.update_order_notification_status(order_id, notification_status)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        return order
    except Exception as error:
        print(str(error))
        sys.stdout.flush()