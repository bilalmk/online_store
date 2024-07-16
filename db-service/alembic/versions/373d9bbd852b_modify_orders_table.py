"""modify orders table

Revision ID: 373d9bbd852b
Revises: 629325b89c3e
Create Date: 2024-07-12 07:18:36.434526

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '373d9bbd852b'
down_revision: Union[str, None] = '629325b89c3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.add_column('orders', sa.Column('order_date', sa.TIMESTAMP, nullable=False))
    op.add_column('orders', sa.Column('shipping_address', sa.String(255), nullable=False))
    op.add_column('orders', sa.Column('billing_address', sa.String(255), nullable=False))
    op.add_column('orders', sa.Column('payment_method', sa.String(50), nullable=False))
    op.add_column('orders', sa.Column('guid', sa.CHAR(36), nullable=False))
    op.add_column('orders', sa.Column('payment_status', sa.String(50), nullable=False, server_default='unpaid'))
    op.add_column('orders', sa.Column('delivery_date', sa.TIMESTAMP, nullable=True))
    op.add_column('orders', sa.Column('delivery_status', sa.String(50), nullable=False, server_default='pending'))
    op.add_column('orders', sa.Column('order_status', sa.String(50), nullable=False, server_default='process'))
    # op.alter_column('orders', 'status', existing_type=sa.String(50), nullable=False, server_default='pending')
    
    op.create_table(
        'order_detail',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('order_guid', sa.CHAR(36),nullable=False),
        sa.Column('order_id', sa.Integer, nullable=False),
        sa.Column('product_id', sa.Integer, nullable=False),
        sa.Column('quantity', sa.Integer, nullable=False),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('discount', sa.Numeric(10, 2), default=0.00),
        sa.Column('total_price', sa.Numeric(10, 2), sa.Computed('quantity * unit_price - discount')),
        sa.Column('create_date', sa.TIMESTAMP, server_default=sa.func.current_timestamp()),
        sa.Column('update_date', sa.TIMESTAMP, server_default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp())
    )


def downgrade() -> None:
    op.drop_column('orders', 'order_date')
    op.drop_column('orders', 'shipping_address')
    op.drop_column('orders', 'billing_address')
    op.drop_column('orders', 'payment_method')
    op.drop_column('orders', 'guid')
    op.drop_column('orders', 'payment_status')
    op.drop_column('orders', 'delivery_date')
    op.drop_column('orders', 'delivery_status')
    op.drop_column('orders', 'order_status')
    op.drop_table("order_detail")
    
    
    # op.alter_column('orders', 'status', existing_type=sa.String(50), nullable=False)
