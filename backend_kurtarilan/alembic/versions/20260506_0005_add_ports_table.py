"""add ports table and port_id to stations

Revision ID: 20260506_0005
Revises: a5b09cf68f19
Create Date: 2026-05-06

"""
from alembic import op
import sqlalchemy as sa

revision = "20260506_0005"
down_revision = "a5b09cf68f19"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. ports tablosunu oluştur
    op.create_table(
        "ports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("city", sa.String(length=128), nullable=False),
        sa.Column("country", sa.String(length=128), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 2. stations tablosuna port_id ekle
    op.add_column(
        "stations",
        sa.Column("port_id", sa.Integer(), sa.ForeignKey("ports.id"), nullable=True),
    )
    op.create_index("ix_stations_port_id", "stations", ["port_id"])


def downgrade() -> None:
    op.drop_index("ix_stations_port_id", table_name="stations")
    op.drop_column("stations", "port_id")
    op.drop_table("ports")
