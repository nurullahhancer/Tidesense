"""add email_notifications_enabled to user

Revision ID: a5b09cf68f19
Revises: a49e0f55c335
Create Date: 2026-05-03 12:30:18.639831
"""
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = 'a5b09cf68f19'
down_revision = 'a49e0f55c335'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('email_notifications_enabled', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('users', 'email_notifications_enabled')
