"""add user login device model

Revision ID: 20260430_0004
Revises: 20260430_0003
Create Date: 2026-04-30 00:20:00
"""

from alembic import op


revision = "20260430_0004"
down_revision = "20260430_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('ALTER TABLE "users" ADD COLUMN IF NOT EXISTS last_login_device_model VARCHAR(128)')


def downgrade() -> None:
    op.execute('ALTER TABLE "users" DROP COLUMN IF EXISTS last_login_device_model')
