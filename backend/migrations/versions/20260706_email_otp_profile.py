"""add email otp and profile fields

Revision ID: 20260706_email_otp
Revises: 5aa2495de664
Create Date: 2026-07-06
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260706_email_otp"
down_revision: Union[str, None] = "5aa2495de664"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(length=32), nullable=True))
    op.add_column("users", sa.Column("email_verified", sa.Boolean(), server_default=sa.true(), nullable=False))
    op.add_column("reports", sa.Column("subject", sa.String(length=180), server_default="User report", nullable=False))
    op.add_column("reports", sa.Column("category", sa.String(length=40), server_default="GENERAL", nullable=False))
    op.create_table(
        "email_otps",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("purpose", sa.String(length=40), nullable=False),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resend_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("consumed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_otps_email", "email_otps", ["email"])
    op.create_index("ix_email_otps_purpose", "email_otps", ["purpose"])
    op.create_index("ix_email_otps_expires_at", "email_otps", ["expires_at"])
    op.create_index("ix_email_otps_consumed", "email_otps", ["consumed"])


def downgrade() -> None:
    op.drop_table("email_otps")
    op.drop_column("reports", "category")
    op.drop_column("reports", "subject")
    op.drop_column("users", "email_verified")
    op.drop_column("users", "phone")
