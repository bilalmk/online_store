"""create payment table

Revision ID: 165b091b7ccd
Revises: 373d9bbd852b
Create Date: 2024-07-19 12:30:16.245554

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
# from sqlalchemy.dialects.mysql import TINYINT


# revision identifiers, used by Alembic.
revision: str = '165b091b7ccd'
down_revision: Union[str, None] = '373d9bbd852b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # op.add_column('orders', sa.Column('notification_status', sa.SMALLINT, nullable=False, server_default=sa.text('0')))
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('order_id', sa.Integer, nullable=False),
        sa.Column('customer_id', sa.Integer, nullable=False),
        sa.Column('transaction_id', sa.CHAR(15), nullable=False),
        sa.Column('payment_gateway', sa.CHAR(255), nullable=False),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('payment_date', sa.DateTime, nullable=False),
        sa.Column('status', sa.SMALLINT, nullable=False, server_default=sa.text('1')),
    )


def downgrade() -> None:
    op.drop_table('payments')
    # op.drop_column('orders', 'notification_status')
