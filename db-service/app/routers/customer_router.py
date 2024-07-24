from shared.models.customer import PublicCustomer
from app.config import sessionDep
from app.crud.customer_crud import Customer_Crud
from fastapi import Depends, HTTPException, APIRouter, Form
from shared.models.customer import LoginRequest
import sys


def get_customer_crud(session: sessionDep) -> Customer_Crud:
    return Customer_Crud(session)

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
)

@router.post("/login", response_model=PublicCustomer)
async def login(login_request: LoginRequest, customer_crud=Depends(get_customer_crud)):
    username = login_request.username
    password = login_request.password
    customer = customer_crud.get_customer(username)

    if not customer:
        raise HTTPException(status_code=404, detail="customer not found")

    customer_crud.varify_password(password, customer.password)
    
    if not customer_crud.varify_password(password, customer.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    return customer

@router.post("/customer", response_model=PublicCustomer)
async def get_customer(customer_id: int = Form(...), customer_crud=Depends(get_customer_crud)):
    customer = customer_crud.get_customer_by_id(customer_id)

    if not customer:
        raise HTTPException(status_code=404, detail="customer not found")

    return customer

@router.get("/", response_model=list[PublicCustomer])
async def get_customers(customer_crud=Depends(get_customer_crud)):
    customers = customer_crud.get_customers()
    if not customers:
        raise HTTPException(status_code=404, detail="customer not found")
    return customers
