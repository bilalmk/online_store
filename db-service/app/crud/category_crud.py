import sys

from fastapi import HTTPException
from shared.models.category import CreateCategory, Category, UpdateCategory
from sqlalchemy.exc import IntegrityError
from sqlmodel import select


class Category_Crud:

    def __init__(self, session):
        self.session = session

    def create_category(self, category: CreateCategory):
        try:
            statement = select(Category).where(Category.guid == category.guid)
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
            print(str(e))
            sys.stdout.flush()
            self.session.rollback()
            return {"status": "failed"}

    def update_category(self, category: UpdateCategory, request_id: str):
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

    def delete_category(self, request_id: str):
        try:

            statement = (
                select(Category).where(Category.guid == request_id).where(Category.status == 1)
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

    def get_category(self, id):
        try:
            statement = select(Category).where(Category.id == id).where(Category.status == 1)
            category = self.session.exec(statement).first()
            if not category:
                return None
            return category
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_category_by_id(self, id):
        try:
            statement = select(Category).where(Category.id == id).where(Category.status == 1)
            category = self.session.exec(statement).first()
            if not category:
                return None
            return category
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_categories(self):
        try:
            statement = select(Category).where(Category.status == 1)
            categories = self.session.exec(statement).all()
            return categories
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
