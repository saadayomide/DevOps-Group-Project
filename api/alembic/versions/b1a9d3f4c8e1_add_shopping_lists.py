"""Add shopping lists tables

Revision ID: b1a9d3f4c8e1
Revises: aa91ec3623ad
Create Date: 2025-12-03 16:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b1a9d3f4c8e1"
down_revision: Union[str, None] = "aa91ec3623ad"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "shopping_lists",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "last_refreshed",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Choose DB types based on dialect to support both PostgreSQL and SQLite
    bind = op.get_bind()
    dialect_name = bind.dialect.name if bind is not None else "sqlite"

    if dialect_name == "postgresql":
        variants_type = postgresql.ARRAY(sa.Text())
        jsonb_type = postgresql.JSONB()
    else:
        # SQLite doesn't have ARRAY/JSONB - use JSON() (stored as text) instead
        variants_type = sa.JSON()
        jsonb_type = sa.JSON()

    op.create_table(
        "shopping_list_items",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "list_id",
            sa.Integer(),
            sa.ForeignKey("shopping_lists.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("category", sa.Text(), nullable=False),
        sa.Column("brand", sa.Text(), nullable=True),
        sa.Column("variants", variants_type, nullable=True),
        sa.Column("quantity", sa.Numeric(10, 3), nullable=False),
        sa.Column("unit", sa.Text(), nullable=False),
        sa.Column("spec_json", jsonb_type, nullable=True),
        sa.Column("best_store", sa.Text(), nullable=True),
        sa.Column("best_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("best_url", sa.Text(), nullable=True),
        sa.Column("comparison_json", jsonb_type, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("shopping_list_items")
    op.drop_table("shopping_lists")
