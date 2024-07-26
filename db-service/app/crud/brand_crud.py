from fastapi import HTTPException
from shared.models.brand import CreateBrand, Brand, UpdateBrand
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

"""
A class to perform CRUD operations for brands in the database.

Args:
    session: The database session to execute queries.

Methods:
    create_brand(brand): Adds a new brand to the database if it doesn't already exist.
    update_brand(brand, request_id): Updates an existing brand's details.
    delete_brand(request_id): Marks a brand as deleted by changing its status.
    get_brand(id): Retrieves a brand by its ID.
    get_brand_by_id(id): Retrieves a brand by its ID.
    get_brands(): Retrieves all active brands.
"""

# This class provides CRUD operations for managing brands in a database.
class Brand_Crud:

    def __init__(self, session):
        # Initializes the class with a database session
        self.session = session

    # creates a new brand in the database
    def create_brand(self, brand: CreateBrand):
        """
        The function creates a new brand in a database, handling cases where the brand already exists,
        encounters integrity errors, or fails for other reasons.
        
        The method first checks if a brand with the same guid
        already exists in the database. If a brand is found, it returns a "exist" status
        
        The possible values for the "status" key are:
        - "exist": If a brand with the same guid already exists in the database.
        - "success": If the brand creation process is successful.
        - "duplicate": If there is an integrity error due to a duplicate entry.
        - "failed": if an exception occurs during the operation
        """
        try:
            statement = select(Brand).where(Brand.guid == brand.guid)
            result = self.session.exec(statement).first()
            if result:
                return {"status": "exist"}

            db_brand = Brand.model_validate(brand)
            self.session.add(db_brand)
            self.session.commit()
            self.session.refresh(db_brand)
            return {"status": "success"}
        except IntegrityError:
            self.session.rollback()
            return {"status": "duplicate"}
        except Exception as e:
            self.session.rollback()
            return {"status": "failed"}

    #  Updates an existing brand information
    def update_brand(self, brand: UpdateBrand, request_id: str):
        """
        This function updates a brand in the database based on the provided brand data and request GUID.
        `request_id` is used to filter the query to find the specific brand based on their `guid` 
        and `status` in the database
        
        returns a dictionary with a status key indicating the outcome of the update operation. 
        The possible status values that can be returned are:
            1. "not-found" if the brand with the provided request_id and active status is not found in the database.
            2. "success-update" if the brand is successfully updated in the database.
            3. "failed-update" if an exception occurs during the operation
        """
        try:
            db_brand: Brand = (
                self.session.query(Brand)
                .filter(Brand.guid == request_id)
                .filter(Brand.status == 1)
                .first()
            )

            if not db_brand:
                return {"status": "not-found"}

            db_brand.sqlmodel_update(brand)
            self.session.add(db_brand)
            self.session.commit()
            self.session.refresh(db_brand)
            return {"status": "success-update"}
        except Exception as e:
            self.session.rollback()
            return {"status": "failed-update"}

    # Soft deletes a brand by setting their status to delete
    def delete_brand(self, request_id: str):
        """
        - This function deletes a brand by changing their status to 2 in the database (soft delete).
        - The `request_id` parameter which is a GUID of the brand that needs to be deleted from the database
        - This request_id will be used to get the brand from database
        - Returns a dictionary with a "status" key indicating the outcome of the operation. 
        - The possible return values are:
            1. "not-found if the brand with the provided request_id is not found in the database.
            2. "success-delete" if the brand is found and successfully marked as deleted (status changed to 2).
            3. "failed-delete" if an exception occurs during the operation
        """
        try:

            statement = (
                select(Brand).where(Brand.guid == request_id).where(Brand.status == 1)
            )
            db_brand = self.session.exec(statement).first()

            if not db_brand:
                return {"status": "not-found"}

            db_brand.status = 2
            self.session.commit()
            return {"status": "success-delete"}

        except Exception as e:
            self.session.rollback()
            return {"status": "failed-delete"}

    # Retrieves a brand by id.
    def get_brand(self, id):
        """
        This function retrieves a brand from the database based on the provided id.
        
        It queries the database to find a brand with the provided id and a active status
        return the brand object or None if brand not found
        """
        try:
            statement = select(Brand).where(Brand.id == id).where(Brand.status == 1)
            brand = self.session.exec(statement).first()
            if not brand:
                return None
            return brand
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Retrieves a brand by id.
    def get_brand_by_id(self, id):
        """
        This function retrieves a brand from the database based on the provided id.
        
        It queries the database to find a brand with the provided id and a active status
        return the brand object or None if brand not found
        """
        try:
            statement = select(Brand).where(Brand.id == id).where(Brand.status == 1)
            brand = self.session.exec(statement).first()
            if not brand:
                return None
            return brand
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Retrieves all active brands.
    def get_brands(self):
        """
        This function retrieves all brands with active status from the database and return this list in response.
        """
        try:
            statement = select(Brand).where(Brand.status == 1)
            brands = self.session.exec(statement).all()
            return brands
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
