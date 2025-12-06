"""add shopping lists and items tables

Revision ID: c3d4e5f6g7
Revises: aa91ec3623ad
Create Date: 2025-12-06 10:40:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "c3d4e5f6g7"
down_revision = "aa91ec3623ad"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shopping_lists",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("owner", sa.String(), nullable=True),
        sa.Column("last_refreshed", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "shopping_list_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("shopping_list_id", sa.Integer(), sa.ForeignKey("shopping_lists.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("brand", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("variants", sa.String(), nullable=True),
        sa.Column("best_store", sa.String(), nullable=True),
        sa.Column("best_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("best_url", sa.String(), nullable=True),
        sa.Column("comparison_json", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("shopping_list_items")
    op.drop_table("shopping_lists")
