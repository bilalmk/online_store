from shared.models.brand import PublicBrand
from app.config import sessionDep
from app.crud.brand_crud import Brand_Crud
from fastapi import Depends, HTTPException, APIRouter, Form

def get_brand_crud(session: sessionDep) -> Brand_Crud:
    return Brand_Crud(session)

router = APIRouter(
    prefix="/brands",
    tags=["brands"],
)

"""
End-Point receives a brand_id as a form input, retrieves the corresponding brand
using a dependency, and returns the brand or raises a 404 error if not found

brand_crud class is a dependency that is used to interact with brand data in the database. 
it contains methods for retrieving brand information
"""
@router.post("/brand", response_model=PublicBrand)
async def get_brand(brand_id: int = Form(...), brand_crud=Depends(get_brand_crud)):
    brand = brand_crud.get_brand_by_id(brand_id)

    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    return brand

"""
End-Point retrieves a list of public brands using a dependency and returns them, 
raising a 404 error if no brands are found

brand_crud class is a dependency that is used to interact with brand data in the database. 
it contains methods for retrieving brand information
"""
@router.get("/", response_model=list[PublicBrand])
async def get_brands(brand_crud=Depends(get_brand_crud)):
    brands = brand_crud.get_brands()
    if not brands:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brands