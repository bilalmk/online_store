import sys
from shared.models.product import PublicProduct
from app.config import sessionDep
from app.crud.product_crud import Product_Crud
from fastapi import Depends, HTTPException, APIRouter, Form
from fastapi import APIRouter


def get_product_crud(session: sessionDep) -> Product_Crud:
    return Product_Crud(session)


router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.post("/product", response_model=PublicProduct)
async def get_product(
    product_id: int = Form(...), product_crud=Depends(get_product_crud)
):
    product = product_crud.get_product_by_id(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.get("/", response_model=list[PublicProduct])
async def get_products(product_crud=Depends(get_product_crud)):
    products = product_crud.get_products()
    if not products:
        raise HTTPException(status_code=404, detail="Product not found")
    return products


@router.post("/product_by_ids", response_model=list[PublicProduct])
async def get_products_by_ids(product_ids: str = Form(...), product_crud=Depends(get_product_crud)):

    product_ids_list = list(map(int, product_ids.split(",")))
    product = product_crud.get_products_by_ids(product_ids_list)

    if not product:
        raise HTTPException(status_code=404, detail="Products not found")

    return product
