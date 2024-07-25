import sys

from fastapi import HTTPException
from shared.models.inventory import InventoryProductUpdate
from shared.models.product import CreateProduct, Product, UpdateProduct
from sqlalchemy.exc import IntegrityError
from sqlmodel import and_, select

"""
The Product_Crud class provides CRUD operations for managing product data in a database. 
It includes methods for creating, updating, deleting, and retrieving products, 
as well as update the inventory.
"""
class Product_Crud:

    def __init__(self, session):
        # Initializes the class with a database session
        self.session = session

    # creates a new product in the database
    def create_product(self, product: CreateProduct):
        """
        The function creates a new product in a database, handling cases where the product already exists,
        encounters integrity errors, or fails for other reasons.
        
        The method first checks if a product with the guid
        already exists in the database. If a product is found, it returns a "exist" status
        
        The possible values for the "status" key are:
        - "exist": If a product with the same guid already exists in the database.
        - "success": If the product creation process is successful.
        - "duplicate": If there is an integrity error due to a duplicate entry.
        - "failed": if an exception occurs during the operation
        """
        try:
            statement = select(Product).where(Product.guid == product.guid)
            result = self.session.exec(statement).first()
            if result:
                return {"status": "exist"}

            db_product = Product.model_validate(product)
            self.session.add(db_product)
            self.session.commit()
            self.session.refresh(db_product)
            return {"status": "success"}
        except IntegrityError:
            self.session.rollback()
            return {"status": "duplicate"}
        except Exception as e:
            print(str(e))
            sys.stdout.flush()
            self.session.rollback()
            return {"status": "failed"}

    #  Updates an existing product information
    def update_product(self, product: UpdateProduct, request_id: str):
        """
        This function updates a product in the database based on the provided product data and request GUID.
        `request_id` is used to filter the query to find the specific product based on their `guid` 
        and `status` in the database
        
        returns a dictionary with a status key indicating the
        outcome of the update operation. The possible status values that can be returned are:
        1. "not-found" if the product with the provided request_id and active status is not found in the database.
        2. "success-update" if the product is successfully updated in the database.
        3. "failed-update" if an exception occurs during the operation
        """
        try:
            db_product: Product = (
                self.session.query(Product)
                .filter(Product.guid == request_id)
                .filter(Product.status == 1)
                .first()
            )

            if not db_product:
                return {"status": "not-found"}

            db_product.sqlmodel_update(product)
            self.session.add(db_product)
            self.session.commit()
            self.session.refresh(db_product)
            return {"status": "success-update"}
        except Exception as e:
            self.session.rollback()
            return {"status": "failed-update"}

    # Soft deletes a product by setting their status to delete
    def delete_product(self, request_id: str):
        """
        - This function deletes a product by changing their status to 2 in the database (soft delete).
        - The `request_id` parameter which is a GUID of the product that needs to be deleted from the database
        - This request_id will be used to get the product from database
        - Returns a dictionary with a "status" key indicating the outcome of the operation. 
        - The possible return values are:
            1. "not-found if the product with the provided request_id is not found in the database.
            2. "success-delete" if the product is found and successfully marked as deleted (status changed to 2).
            3. "failed-delete" if an exception occurs during the operation
        """
        try:

            statement = (
                select(Product)
                .where(Product.guid == request_id)
                .where(Product.status == 1)
            )
            db_product = self.session.exec(statement).first()

            if not db_product:
                return {"status": "not-found"}

            db_product.status = 2
            self.session.commit()
            return {"status": "success-delete"}

        except Exception as e:
            self.session.rollback()
            return {"status": "failed-delete"}

    # Retrieves a product by product id.
    def get_product(self, id):
        """
        This function retrieves a product from the database based on the provided id.
        
        It queries the database to find a product with the provided id and a active status
        return the product object or None if product not found
        """
        try:
            statement = (
                select(Product).where(Product.id == id).where(Product.status == 1)
            )
            product = self.session.exec(statement).first()
            if not product:
                return None
            return product
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Retrieves a product by product id.
    def get_product_by_id(self, id):
        """
        This function retrieves a product from the database based on the provided id.
        
        It queries the database to find a product with the provided id and a active status
        return the product object or None if product not found
        """
        try:
            statement = (
                select(Product).where(Product.id == id).where(Product.status == 1)
            )
            product = self.session.exec(statement).first()
            if not product:
                return None
            return product
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Retrieves all active products.
    def get_products(self):
        """
        This function retrieves all products with active status from the database and return this list in response.
        """
        try:
            statement = select(Product).where(Product.status == 1)
            products = self.session.exec(statement).all()
            return products
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Retrieves a list of products by product ids.
    def get_products_by_ids(self, ids):
        """
        This function retrieves a list of products from the database based on the provided list of ids.
        
        It queries the database to find a products with the provided ids and a active status
        return the products list or raise 500 http error
        """
        try:
            statement = select(Product).where(and_(Product.status == 1, Product.id.in_(ids)))  # type: ignore
            products = self.session.exec(statement).all()
            return products
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # update product stock quantity after creating an order
    def update_inventory(self, inventory_info: list[InventoryProductUpdate]):
        """
        This function updates the stock quantity of products in the database based on
        the information provided in the `inventory_info` list.
        
        This method takes a list of `InventoryProductUpdate`
        objects as input in the `inventory_info` parameter. Each `InventoryProductUpdate` object
        contains information about a product update, such as the `product_id` and the `quantity` to be
        updated
        
        - The possible return values are:
            1. "not-found if the product with the provided product_id is not found in the database.
            2. "success-update" if the product is found and successfully update the records.
            3. "failed-update" if an exception occurs during the operation
        """
        try:
            # print("update_inventory_db_function")
            # sys.stdout.flush()
            # print(inventory_info)
            # sys.stdout.flush()
            for info in inventory_info:
                # print("inside loop")
                # sys.stdout.flush()
                # print(info)
                # sys.stdout.flush()
                db_product: Product = (
                    self.session.query(Product)
                    .filter(Product.id == info.product_id)
                    .filter(Product.status == 1)
                    .first()
                )

                if not db_product:
                    return {"status": "not-found"}

                db_product.stock_quantity = db_product.stock_quantity - info.quantity
                self.session.add(db_product)

            self.session.commit()
            return {"status": "success-update"}
        except Exception as e:
            print("execption from crud")
            sys.stdout.flush()
            print(str(e))
            sys.stdout.flush()
            self.session.rollback()
            return {"status": "failed-update"}
