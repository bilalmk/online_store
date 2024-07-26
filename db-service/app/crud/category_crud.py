from fastapi import HTTPException
from shared.models.category import CreateCategory, Category, UpdateCategory
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

"""
A class to perform CRUD operations for categories in the database.

Args:
    session: The database session to execute queries.

Methods:
    create_category(category): Adds a new category to the database if it doesn't already exist.
    update_category(category, request_id): Updates an existing category's details.
    delete_category(request_id): Marks a category as deleted by changing its status.
    get_category(id): Retrieves a category by its ID.
    get_category_by_id(id): Retrieves a category by its ID.
    get_categories(): Retrieves all active categories.
"""

# This class provides CRUD operations for managing categories in a database.
class Category_Crud:

    def __init__(self, session):
        # Initializes the class with a database session
        self.session = session

    # creates a new category in the database
    def create_category(self, category: CreateCategory):
        """
        The function creates a new category in a database, handling cases where the category already exists,
        encounters integrity errors, or fails for other reasons.
        
        The method first checks if a category with the same parent_id and category_name
        already exists in the database. If a category is found, it returns a "exist" status
        
        The possible values for the "status" key are:
        - "exist": If a category with the same guid already exists in the database.
        - "success": If the category creation process is successful.
        - "duplicate": If there is an integrity error due to a duplicate entry.
        - "failed": if an exception occurs during the operation
        """
        try:
            # statement = select(Category).where(Category.guid == category.guid)
            statement = (
                select(Category)
                .where(Category.parent_id == category.parent_id)
                .where(Category.category_name == category.category_name)
                .where(Category.status != 2)
            )
            result = self.session.exec(statement).first()
            if result:
                return {"status": "exist"}

            db_category = Category.model_validate(category)
            self.session.add(db_category)
            self.session.commit()
            self.session.refresh(db_category)
            return {"status": "success"}
        except IntegrityError:
            self.session.rollback()
            return {"status": "duplicate"}
        except Exception as e:
            self.session.rollback()
            return {"status": "failed"}

    #  Updates an existing category information
    def update_category(self, category: UpdateCategory, request_id: str):
        """
        This function updates a category in the database based on the provided category data and request GUID.
        `request_id` is used to filter the query to find the specific category based on their `guid` 
        and `status` in the database
        
        returns a dictionary with a status key indicating the outcome of the update operation. 
        The possible status values that can be returned are:
            1. "not-found" if the category with the provided request_id and active status is not found in the database.
            2. "success-update" if the category is successfully updated in the database.
            3. "failed-update" if an exception occurs during the operation
        """
        try:
            db_category: Category = (
                self.session.query(Category)
                .filter(Category.guid == request_id)
                .filter(Category.status == 1)
                .first()
            )

            if not db_category:
                return {"status": "not-found"}

            db_category.sqlmodel_update(category)
            self.session.add(db_category)
            self.session.commit()
            self.session.refresh(db_category)
            return {"status": "success-update"}
        except Exception as e:
            self.session.rollback()
            return {"status": "failed-update"}

    # Soft deletes a category by setting their status to delete
    def delete_category(self, request_id: str):
        """
        - This function deletes a category by changing their status to 2 in the database (soft delete).
        - The `request_id` parameter which is a GUID of the category that needs to be deleted from the database
        - This request_id will be used to get the category from database
        - Returns a dictionary with a "status" key indicating the outcome of the operation. 
        - The possible return values are:
            1. "not-found if the category with the provided request_id is not found in the database.
            2. "success-delete" if the category is found and successfully marked as deleted (status changed to 2).
            3. "failed-delete" if an exception occurs during the operation
        """
        try:

            statement = (
                select(Category)
                .where(Category.guid == request_id)
                .where(Category.status == 1)
            )
            db_category = self.session.exec(statement).first()

            if not db_category:
                return {"status": "not-found"}

            db_category.status = 2
            self.session.commit()
            return {"status": "success-delete"}

        except Exception as e:
            self.session.rollback()
            return {"status": "failed-delete"}

    # Retrieves a category by id.
    def get_category(self, id):
        """
        This function retrieves a category from the database based on the provided id.
        
        It queries the database to find a category with the provided id and a active status
        return the category object or None if category not found
        """
        try:
            statement = (
                select(Category).where(Category.id == id).where(Category.status == 1)
            )
            category = self.session.exec(statement).first()
            if not category:
                return None
            return category
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Retrieves a category by id.
    def get_category_by_id(self, id):
        """
        This function retrieves a category from the database based on the provided id.
        
        It queries the database to find a category with the provided id and a active status
        return the category object or None if category not found
        """
        try:
            statement = (
                select(Category).where(Category.id == id).where(Category.status == 1)
            )
            category = self.session.exec(statement).first()
            if not category:
                return None
            return category
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Retrieves all active categories.
    def get_categories(self):
        """
        This function retrieves all categories with active status from the database and return this list in response.
        """
        try:
            statement = select(Category).where(Category.status == 1)
            categories = self.session.exec(statement).all()
            return categories
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
