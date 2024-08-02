"""add initial admin data

Revision ID: d23929f7fe5a
Revises: f807e302632a
Create Date: 2024-08-02 18:11:09.810572

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = 'd23929f7fe5a'
down_revision: Union[str, None] = 'f807e302632a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('applications')
    op.drop_table('status_delivery')
    op.drop_table('subjects')
    op.alter_column('users', 'role',
               existing_type=postgresql.ENUM('admin', 'user', name='roleenum'),
               nullable=True,
               existing_server_default=sa.text("'user'::roleenum"))
    conn = op.get_bind()
    conn.execute(
        text("INSERT INTO users (username, hashed_password, role) VALUES (:username, :password, :role)"),
        {"username": "admin1", "password": "hashed_password1", "role": "admin"}
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'role',
               existing_type=postgresql.ENUM('admin', 'user', name='roleenum'),
               nullable=False,
               existing_server_default=sa.text("'user'::roleenum"))
    op.create_table('subjects',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('teacher', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('cabinet', sa.INTEGER(), autoincrement=False, nullable=True)
    )
    op.create_table('status_delivery',
    sa.Column('docid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('itemid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('status_type', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('status_pop', sa.VARCHAR(length=100), autoincrement=False, nullable=True)
    )
    op.create_table('applications',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('kind', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('version', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('state', postgresql.ENUM('NEW', 'INSTALLING', 'RUNNING', name='app_state'), autoincrement=False, nullable=True),
    sa.Column('json_data', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='applications_pkey')
    )

    conn = op.get_bind()
    conn.execute(
        text("DELETE FROM users WHERE username = :username"),
        {"username": "admin1"}
    )
    # ### end Alembic commands ###
