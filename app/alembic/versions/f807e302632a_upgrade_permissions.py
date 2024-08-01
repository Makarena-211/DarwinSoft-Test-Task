"""upgrade permissions

Revision ID: f807e302632a
Revises: 14e623a2aaba
Create Date: 2024-08-01 18:22:57.477873

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f807e302632a'
down_revision: Union[str, None] = '14e623a2aaba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('permissions', sa.Column('can_write', sa.Boolean))


def downgrade() -> None:
    pass
