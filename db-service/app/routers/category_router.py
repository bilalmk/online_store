from shared.models.category import PublicCategory
from app.config import sessionDep
from app.crud.category_crud import Category_Crud
from fastapi import Depends, HTTPException, APIRouter, Form
from fastapi import APIRouter

def get_category_crud(session: sessionDep) -> Category_Crud:
    return Category_Crud(session)

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)

@router.post("/category", response_model=PublicCategory)
async def get_category(category_id: int = Form(...), category_crud=Depends(get_category_crud)):
    category = category_crud.get_category_by_id(category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category

@router.get("/", response_model=list[PublicCategory])
async def get_categories(category_crud=Depends(get_category_crud)):
    categories = category_crud.get_categories()
    if not categories:
        raise HTTPException(status_code=404, detail="Category not found")
    return categories