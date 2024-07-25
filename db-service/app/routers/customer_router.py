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

"""
End-Point handles customer login by verifying the username and password provided in the
request,against stored customer data

customer_crud is a dependency that is used to interact with customer data in the database. 
it contains methods for retrieving customer information and verifying passwords
"""
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

"""
- End-Point retrieves a customer by ID and returns a PublicCustomer model, 
raising a 404 error if the customer is not found

- customer_crud class is a dependency that is used to interact with customer data in the database. 
it contains methods for retrieving customer information
"""
@router.post("/customer", response_model=PublicCustomer)
async def get_customer(customer_id: int = Form(...), customer_crud=Depends(get_customer_crud)):
    customer = customer_crud.get_customer_by_id(customer_id)

    if not customer:
        raise HTTPException(status_code=404, detail="customer not found")

    return customer


"""
- End-Point retrieves a list of customers and returns them as a response, 
raising a 404 error if no customers are found

- customer_crud class is a dependency that is used to interact with customer data in the database.
it contains methods for retrieving customer information
"""
@router.get("/", response_model=list[PublicCustomer])
async def get_customers(customer_crud=Depends(get_customer_crud)):
    customers = customer_crud.get_customers()
    if not customers:
        raise HTTPException(status_code=404, detail="customer not found")
    return customers
