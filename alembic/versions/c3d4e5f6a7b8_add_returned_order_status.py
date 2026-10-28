"""add RETURNED to OrderStatus enum

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-10-27 22:23:33.507000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE orderstatus ADD VALUE 'RETURNED' AFTER 'DELIVERED'")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TYPE orderstatus RENAME TO orderstatus_old")
    op.execute(
        "CREATE TYPE orderstatus AS ENUM "
        "('RECEIVED', 'PROCESSING', 'FULFILLED', 'SHIPPED', 'DELIVERED', 'CANCELLED')"
    )
    op.execute(
        "ALTER TABLE orders ALTER COLUMN status TYPE orderstatus "
        "USING status::text::orderstatus"
    )
    op.execute("DROP TYPE orderstatus_old")
