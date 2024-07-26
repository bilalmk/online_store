from shared.models.category import PublicCategory
from app.config import sessionDep
from app.crud.category_crud import Category_Crud
from fastapi import Depends, HTTPException, APIRouter, Form

def get_category_crud(session: sessionDep) -> Category_Crud:
    return Category_Crud(session)

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)

"""
End-Point receives a category_id as a form input, retrieves the corresponding category
using a dependency, and returns the category or raises a 404 error if not found

category_crud class is a dependency that is used to interact with category data in the database. 
it contains methods for retrieving category information
"""
@router.post("/category", response_model=PublicCategory)
async def get_category(category_id: int = Form(...), category_crud=Depends(get_category_crud)):
    category = category_crud.get_category_by_id(category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


"""
End-Point retrieves a list of public categories using a dependency and returns them, 
raising a 404 error if no categories are found

category_crud class is a dependency that is used to interact with category data in the database. 
it contains methods for retrieving category information
"""
@router.get("/", response_model=list[PublicCategory])
async def get_categories(category_crud=Depends(get_category_crud)):
    categories = category_crud.get_categories()
    if not categories:
        raise HTTPException(status_code=404, detail="Category not found")
    return categories