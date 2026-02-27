"""Add competence unique constraint and simplify user_competencies.

Revision ID: 4a7c9d5f2b11
Revises: 9d3b6f2a4c11
Create Date: 2026-02-27 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4a7c9d5f2b11"
down_revision: str | Sequence[str] | None = "9d3b6f2a4c11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("competencies") as batch_op:
        batch_op.create_unique_constraint("uq_competencies_name", ["name"])

    with op.batch_alter_table("user_competencies") as batch_op:
        batch_op.drop_column("is_active")
        batch_op.create_index("ix_user_competencies_competence_id", ["competence_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("user_competencies") as batch_op:
        batch_op.drop_index("ix_user_competencies_competence_id")
        batch_op.add_column(sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.alter_column("is_active", server_default=None)

    with op.batch_alter_table("competencies") as batch_op:
        batch_op.drop_constraint("uq_competencies_name", type_="unique")
