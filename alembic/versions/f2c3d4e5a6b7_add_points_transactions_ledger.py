"""Add points transactions ledger table.

Revision ID: f2c3d4e5a6b7
Revises: 4a7c9d5f2b11
Create Date: 2026-04-02 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f2c3d4e5a6b7"
down_revision: str | Sequence[str] | None = "4a7c9d5f2b11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "points_transactions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("recipient_id", sa.Integer(), nullable=False),
        sa.Column("giver_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("points_type", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["giver_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["recipient_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_points_transactions_recipient_created_at",
        "points_transactions",
        ["recipient_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_points_transactions_points_type_created_at",
        "points_transactions",
        ["points_type", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_points_transactions_points_type_created_at", table_name="points_transactions")
    op.drop_index("ix_points_transactions_recipient_created_at", table_name="points_transactions")
    op.drop_table("points_transactions")
