"""add artist url page

Revision ID: 5925ebf1815b
Revises: 9ce6cfa46dd2
Create Date: 2026-02-15 23:43:52.554737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5925ebf1815b'
down_revision: Union[str, Sequence[str], None] = '9ce6cfa46dd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'artists',
        sa.Column('artist_url', sa.String(500), nullable=True)
    )
    op.add_column(
        'releases',
        sa.Column('release_url', sa.String(500), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('artists', 'artist_url')
    op.drop_column('releases', 'release_url')
