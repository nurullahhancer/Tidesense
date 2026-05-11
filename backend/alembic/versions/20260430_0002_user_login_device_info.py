"""add user login device info

Revision ID: 20260430_0002
Revises: 20260424_0001
Create Date: 2026-04-30 00:00:00
"""

from alembic import op


revision = "20260430_0002"
down_revision = "20260424_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('ALTER TABLE "users" ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ')
    op.execute('ALTER TABLE "users" ADD COLUMN IF NOT EXISTS last_login_ip VARCHAR(64)')
    op.execute('ALTER TABLE "users" ADD COLUMN IF NOT EXISTS last_login_user_agent VARCHAR(512)')
    op.execute('ALTER TABLE "users" ADD COLUMN IF NOT EXISTS last_login_device VARCHAR(128)')
    op.execute('ALTER TABLE "users" ADD COLUMN IF NOT EXISTS last_login_os VARCHAR(128)')
    op.execute('ALTER TABLE "users" ADD COLUMN IF NOT EXISTS last_login_browser VARCHAR(128)')


def downgrade() -> None:
    op.drop_column("users", "last_login_browser")
    op.drop_column("users", "last_login_os")
    op.drop_column("users", "last_login_device")
    op.drop_column("users", "last_login_user_agent")
    op.drop_column("users", "last_login_ip")
    op.drop_column("users", "last_login_at")
