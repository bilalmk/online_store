import sys
from shared.models.payment import CreatePayment, PublicPayment
from app.config import sessionDep
from app.crud.payment_crud import Payment_Crud
from fastapi import Depends, HTTPException, APIRouter, Form


def get_payment_crud(session: sessionDep) -> Payment_Crud:
    return Payment_Crud(session)

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)


@router.post("/create")
async def post_payment(payment: CreatePayment, payment_crud=Depends(get_payment_crud)):
    try:
        response = payment_crud.create_payment(payment)
        if not response:
            raise HTTPException(status_code=404, detail="Payment not found")

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

