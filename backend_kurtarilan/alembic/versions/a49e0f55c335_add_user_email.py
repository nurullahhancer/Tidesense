"""add user email

Revision ID: a49e0f55c335
Revises: 20260430_0004
Create Date: 2026-05-03 07:59:32.263046
"""
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = 'a49e0f55c335'
down_revision = '20260430_0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('email', sa.String(length=255), nullable=True))
    op.create_unique_constraint('uq_users_email', 'users', ['email'])


def downgrade() -> None:
    op.drop_constraint('uq_users_email', 'users', type_='unique')
    op.drop_column('users', 'email')
