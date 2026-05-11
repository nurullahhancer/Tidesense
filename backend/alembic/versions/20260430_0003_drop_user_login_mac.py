"""drop user login mac

Revision ID: 20260430_0003
Revises: 20260430_0002
Create Date: 2026-04-30 00:10:00
"""

from alembic import op


revision = "20260430_0003"
down_revision = "20260430_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('ALTER TABLE "users" DROP COLUMN IF EXISTS last_login_mac')


def downgrade() -> None:
    op.execute('ALTER TABLE "users" ADD COLUMN IF NOT EXISTS last_login_mac VARCHAR(32)')
