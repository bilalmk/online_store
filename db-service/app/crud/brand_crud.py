import sys

from fastapi import HTTPException
from shared.models.brand import CreateBrand, Brand, UpdateBrand
from sqlalchemy.exc import IntegrityError
from sqlmodel import select


class Brand_Crud:

    def __init__(self, session):
        self.session = session

    def create_brand(self, brand: CreateBrand):
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
            print(str(e))
            sys.stdout.flush()
            self.session.rollback()
            return {"status": "failed"}

    def update_brand(self, brand: UpdateBrand, request_id: str):
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

    def delete_brand(self, request_id: str):
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

    def get_brand(self, id):
        try:
            statement = select(Brand).where(Brand.id == id).where(Brand.status == 1)
            brand = self.session.exec(statement).first()
            if not brand:
                return None
            return brand
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_brand_by_id(self, id):
        try:
            statement = select(Brand).where(Brand.id == id).where(Brand.status == 1)
            brand = self.session.exec(statement).first()
            if not brand:
                return None
            return brand
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_brands(self):
        try:
            statement = select(Brand).where(Brand.status == 1)
            brands = self.session.exec(statement).all()
            return brands
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
