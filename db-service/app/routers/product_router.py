import sys
from shared.models.inventory import InventoryProductUpdate
from shared.models.product import PublicProduct
from app.config import sessionDep
from app.crud.product_crud import Product_Crud
from fastapi import Depends, HTTPException, APIRouter, Form


def get_product_crud(session: sessionDep) -> Product_Crud:
    return Product_Crud(session)


router = APIRouter(
    prefix="/products",
    tags=["products"],
)

"""
End-Point receives a product_id as a form input, retrieves the corresponding product
using a dependency, and returns the product or raises a 404 error if not found

product_crud class is a dependency that is used to interact with product data in the database. 
it contains methods for retrieving product information
"""
@router.post("/product", response_model=PublicProduct)
async def get_product(
    product_id: int = Form(...), product_crud=Depends(get_product_crud)
):
    product = product_crud.get_product_by_id(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


"""
End-Point retrieves a list of public products using a dependency and returns them, 
raising a 404 error if no products are found

product_crud class is a dependency that is used to interact with product data in the database. 
it contains methods for retrieving product information
"""
@router.get("/", response_model=list[PublicProduct])
async def get_products(product_crud=Depends(get_product_crud)):
    products = product_crud.get_products()
    if not products:
        raise HTTPException(status_code=404, detail="Product not found")
    return products


"""
End-Point retrieves a list of public products by their IDs, IDs are receiving in request in comma separated string,
using a dependency and returns them as response. Raising a 404 error if no products are found

product_crud class is a dependency that is used to interact with product data in the database.
it contains methods for retrieving product information
"""
@router.post("/product_by_ids", response_model=list[PublicProduct])    
async def get_products_by_ids(product_ids: str = Form(...), product_crud=Depends(get_product_crud)):

    """generate list of ids from comma separated string of input ids"""
    product_ids_list = list(map(int, product_ids.split(",")))
    product = product_crud.get_products_by_ids(product_ids_list)

    if not product:
        raise HTTPException(status_code=404, detail="Products not found")

    return product

"""
End-Point updates inventory information using a dependency, for a list of products and handles exceptions by
returning a 404 status code if the product is not found

product_crud class is a dependency that is used to interact with product data in the database.
it contains methods for updating product information

This end-point is called from the inventory microservice to update inventory information, after successfully 
created the order and received its payment

"""
@router.put("/inventory")
async def update_inventory(inventory_info: list[InventoryProductUpdate], product_crud=Depends(get_product_crud)):
    try:
        # print("inventory_info")
        # sys.stdout.flush()
        product = product_crud.update_inventory(inventory_info)
        # print("product")
        # sys.stdout.flush()
        # print(product)
        # sys.stdout.flush()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        print("Exception from route")
        sys.stdout.flush()
        print(str(e))
        sys.stdout.flush()

    return product
