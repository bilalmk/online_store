"""create database tables

Revision ID: 629325b89c3e
Revises: 
Create Date: 2024-06-27 20:35:24.801393

"""

from typing import Sequence, Union
#from sqlalchemy.dialects.mysql import DECIMAL
from alembic import op  # type: ignore
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "629325b89c3e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id", sa.Integer, primary_key=True, nullable=False, autoincrement=True
        ),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(100), nullable=False, unique=True),
        sa.Column("password", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(50)),
        sa.Column("last_name", sa.String(50)),
        sa.Column("address", sa.String(255)),
        sa.Column("phone_number", sa.String(20)),
        sa.Column("guid", sa.CHAR(36), nullable=False),
        sa.Column("status", sa.SMALLINT, nullable=False, server_default=sa.text('1')),
        sa.Column(
            "created_at", sa.TIMESTAMP, server_default=sa.func.current_timestamp()
        ),
    )

    op.create_table(
        "addresses",
        sa.Column(
            "id", sa.Integer, primary_key=True, nullable=False, autoincrement=True
        ),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("address", sa.String(255), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("postal_code", sa.String(20), nullable=False),
        sa.Column("country", sa.String(100), nullable=False),
    )

    # Creating table `brands`
    op.create_table(
        "brands",
        sa.Column(
            "id", sa.Integer, primary_key=True, nullable=False, autoincrement=True
        ),
        sa.Column("brand_name", sa.String(255), nullable=False, unique=True),
        sa.Column("brand_slug", sa.String(255), nullable=False, unique=True),
        sa.Column("guid", sa.CHAR(36), nullable=False),
        sa.Column("created_by", sa.Integer, nullable=False),
        sa.Column(
            "created_at", sa.TIMESTAMP, server_default=sa.func.current_timestamp()
        ),
        sa.Column("status", sa.SMALLINT, nullable=False, server_default="1")
    )

    # Creating table `categories`
    op.create_table(
        "categories",
        sa.Column(
            "id", sa.Integer, primary_key=True, nullable=False, autoincrement=True
        ),
        sa.Column("parent_id", sa.Integer, default=0),
        sa.Column("category_name", sa.String(255), nullable=False),
        sa.Column("category_slug", sa.String(255), nullable=False),
        sa.Column("guid", sa.CHAR(36), nullable=False),
        sa.Column("created_by", sa.Integer, nullable=False),
        sa.Column(
            "created_at", sa.TIMESTAMP, server_default=sa.func.current_timestamp()
        ),
        sa.Column("status", sa.SMALLINT, nullable=False, server_default="1")
    )

    # Creating table `orderitems`
    # op.create_table(
    #     "orderitems",
    #     sa.Column(
    #         "id", sa.Integer, primary_key=True, nullable=False, autoincrement=True
    #     ),
    #     sa.Column("order_id", sa.Integer),
    #     sa.Column("product_id", sa.Integer),
    #     sa.Column("quantity", sa.Integer, nullable=False),
    #     sa.Column("price", sa.Numeric(10, 2), nullable=False),
    # )

    # Creating table `orders`
    op.create_table(
        "orders",
        sa.Column(
            "order_id", sa.Integer, primary_key=True, nullable=False, autoincrement=True
        ),
        sa.Column("customer_id", sa.Integer),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.SMALLINT, nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at", sa.TIMESTAMP, server_default=sa.func.current_timestamp()
        ),
    )

    # Creating table `products`
    op.create_table(
        "products",
        sa.Column(
            "id", sa.Integer, primary_key=True, nullable=False, autoincrement=True
        ),
        sa.Column("name", sa.String(2000), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("stock_quantity", sa.Integer, nullable=False),
        sa.Column("category_id", sa.Integer, nullable=False),
        sa.Column("brand_id", sa.Integer, nullable=False),
        sa.Column("image_name", sa.String(1000), nullable=True),
        sa.Column("guid", sa.CHAR(36), nullable=False),
        sa.Column("status", sa.SMALLINT, nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at", sa.TIMESTAMP, server_default=sa.func.current_timestamp()
        ),
        sa.Column("created_by", sa.Integer, nullable=False),
    )

    # Creating table `shoppingcart`
    op.create_table(
        "shoppingcart",
        sa.Column(
            "id", sa.Integer, primary_key=True, nullable=False, autoincrement=True
        ),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id")),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("added_at", sa.TIMESTAMP, server_default=sa.func.current_timestamp()),
    )

    # Creating table `users`


def downgrade() -> None:
    op.drop_table("shoppingcart")
    op.drop_table("products")
    op.drop_table("orders")
    op.drop_table("categories")
    op.drop_table("brands")
    op.drop_table("addresses")
    op.drop_table("users")
