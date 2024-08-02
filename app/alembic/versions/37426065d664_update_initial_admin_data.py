"""update initial admin data

Revision ID: 37426065d664
Revises: d23929f7fe5a
Create Date: 2024-08-02 18:16:58.193640

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
from auth import get_password_hash

# revision identifiers, used by Alembic.
revision: str = '37426065d664'
down_revision: Union[str, None] = 'd23929f7fe5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    new_hashed_password = get_password_hash('admin1') 
    conn = op.get_bind()
    conn.execute(
        text("UPDATE users SET hashed_password = :password WHERE username = :username"),
        {"username": "admin1", "password": new_hashed_password}
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
