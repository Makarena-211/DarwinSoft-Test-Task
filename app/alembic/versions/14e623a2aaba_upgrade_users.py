"""upgrade users

Revision ID: 14e623a2aaba
Revises: 7f5d3d50b030
Create Date: 2024-08-01 15:25:16.295533

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14e623a2aaba'
down_revision: Union[str, None] = '7f5d3d50b030'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
     op.add_column('users', sa.Column('role', sa.Enum('admin', 'user', name='roleenum'), nullable=False, server_default='user'))


def downgrade() -> None:
    pass
