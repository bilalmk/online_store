from shared.models.brand import PublicBrand
from app.config import sessionDep
from app.crud.brand_crud import Brand_Crud
from fastapi import Depends, HTTPException, APIRouter, Form
from fastapi import APIRouter

def get_brand_crud(session: sessionDep) -> Brand_Crud:
    return Brand_Crud(session)

router = APIRouter(
    prefix="/brands",
    tags=["brands"],
)

@router.post("/brand", response_model=PublicBrand)
async def get_brand(brand_id: int = Form(...), brand_crud=Depends(get_brand_crud)):
    brand = brand_crud.get_brand_by_id(brand_id)

    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    return brand

@router.get("/", response_model=list[PublicBrand])
async def get_brands(brand_crud=Depends(get_brand_crud)):
    brands = brand_crud.get_brands()
    if not brands:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brands