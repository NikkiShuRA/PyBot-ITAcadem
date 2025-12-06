"""Splited points in to the nullable academic and reputaion_points

Revision ID: 0786cd4e28e9
Revises: 4945016c09ea
Create Date: 2025-12-06 21:54:14.397453

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "0786cd4e28e9"
down_revision: str | Sequence[str] | None = "4945016c09ea"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
