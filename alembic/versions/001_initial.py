"""create listings and orders tables

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "listings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("seller_id", UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("crop_type", sa.String(100), nullable=False),
        sa.Column("quantity_kg", sa.Float, nullable=False),
        sa.Column("price_per_kg", sa.Float, nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_listings_seller_id", "listings", ["seller_id"])

    op.create_table(
        "orders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("listing_id", UUID(as_uuid=True), sa.ForeignKey("listings.id"), nullable=False),
        sa.Column("buyer_id", UUID(as_uuid=True), nullable=False),
        sa.Column("seller_id", UUID(as_uuid=True), nullable=False),
        sa.Column("quantity_kg", sa.Float, nullable=False),
        sa.Column("total_price", sa.Float, nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_orders_buyer_id", "orders", ["buyer_id"])
    op.create_index("ix_orders_seller_id", "orders", ["seller_id"])


def downgrade() -> None:
    op.drop_index("ix_orders_seller_id")
    op.drop_index("ix_orders_buyer_id")
    op.drop_table("orders")
    op.drop_index("ix_listings_seller_id")
    op.drop_table("listings")
