import sys

from fastapi import HTTPException
from shared.models.product import CreateProduct, Product, UpdateProduct
from sqlalchemy.exc import IntegrityError
from sqlmodel import select


class Product_Crud:

    def __init__(self, session):
        self.session = session

    def create_product(self, product: CreateProduct):
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

    def update_product(self, product: UpdateProduct, request_id: str):
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

    def delete_product(self, request_id: str):
        try:

            statement = (
                select(Product).where(Product.guid == request_id).where(Product.status == 1)
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

    def get_product(self, id):
        try:
            statement = select(Product).where(Product.id == id).where(Product.status == 1)
            product = self.session.exec(statement).first()
            if not product:
                return None
            return product
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_product_by_id(self, id):
        try:
            statement = select(Product).where(Product.id == id).where(Product.status == 1)
            product = self.session.exec(statement).first()
            if not product:
                return None
            return product
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_products(self):
        try:
            statement = select(Product).where(Product.status == 1)
            products = self.session.exec(statement).all()
            return products
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
