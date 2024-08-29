"""initial

Revision ID: cb9dda281d95
Revises: 
Create Date: 2024-08-29 12:10:06.839718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'cb9dda281d95'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('refreshtoken',
                    sa.Column('token', sa.String(length=512), nullable=False),
                    sa.Column('expiration_date', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('id', sa.Uuid(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('token')
                    )
    op.create_table('role',
                    sa.Column('name', sa.String(length=256), nullable=False),
                    sa.Column('id', sa.Uuid(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
                    )
    op.create_table('user',
                    sa.Column('login', sa.String(length=256), nullable=False),
                    sa.Column('email', sa.String(length=256), nullable=False),
                    sa.Column('password', sa.String(length=256), nullable=False),
                    sa.Column('salt', sa.LargeBinary(length=512), nullable=False),
                    sa.Column('is_active', sa.Boolean(), nullable=False),
                    sa.Column('is_staff', sa.Boolean(), nullable=False),
                    sa.Column('is_super_user', sa.Boolean(), nullable=False),
                    sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
                    sa.Column('id', sa.Uuid(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email'),
                    sa.UniqueConstraint('login')
                    )
    op.create_table('session',
                    sa.Column('user_id', sa.Uuid(), nullable=False),
                    sa.Column('refresh_token_id', sa.Uuid(), nullable=False),
                    sa.Column('user_agent', sa.String(length=512), nullable=False),
                    sa.Column('id', sa.Uuid(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
                    sa.ForeignKeyConstraint(['refresh_token_id'], ['refreshtoken.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('user_agent')
                    )
    op.create_table('user_role',
                    sa.Column('user_id', sa.Uuid(), nullable=False),
                    sa.Column('role_id', sa.Uuid(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
                    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('user_id', 'role_id'),
                    sa.UniqueConstraint('user_id', 'role_id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_role')
    op.drop_table('session')
    op.drop_table('user')
    op.drop_table('role')
    op.drop_table('refreshtoken')
    # ### end Alembic commands ###
