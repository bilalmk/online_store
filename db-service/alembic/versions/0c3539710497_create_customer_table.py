"""create customer table

Revision ID: 0c3539710497
Revises: 165b091b7ccd
Create Date: 2024-07-24 12:52:08.697008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c3539710497'
down_revision: Union[str, None] = '165b091b7ccd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "customers",
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
        sa.Column("status", sa.SMALLINT, nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at", sa.TIMESTAMP, server_default=sa.func.current_timestamp()
        ),
    )


def downgrade() -> None:
    op.drop_table("customers")
