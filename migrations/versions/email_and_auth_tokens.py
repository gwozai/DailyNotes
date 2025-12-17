"""Add email to user and auth_token/rate_limit tables

Revision ID: email_auth_tokens_001
Revises: week_start_monday_001
Create Date: 2025-12-16 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from app.model_types import GUID


# revision identifiers, used by Alembic.
revision = "email_auth_tokens_001"
down_revision = "week_start_monday_001"
branch_labels = None
depends_on = None


def upgrade():
    # Add email column to user table
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("email", sa.LargeBinary(), nullable=True))

    # Create auth_token table
    op.create_table(
        "auth_token",
        sa.Column("uuid", GUID(), nullable=False),
        sa.Column("user_id", GUID(), nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False),
        sa.Column("token_type", sa.String(32), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("uuid"),
        sa.ForeignKeyConstraint(["user_id"], ["user.uuid"], ondelete="CASCADE"),
    )
    op.create_index("ix_auth_token_uuid", "auth_token", ["uuid"], unique=True)
    op.create_index("ix_auth_token_token_hash", "auth_token", ["token_hash"])

    # Create rate_limit table
    op.create_table(
        "rate_limit",
        sa.Column("uuid", GUID(), nullable=False),
        sa.Column("identifier", sa.String(256), nullable=False),
        sa.Column("action_type", sa.String(32), nullable=False),
        sa.Column(
            "timestamp", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("uuid"),
    )
    op.create_index("ix_rate_limit_uuid", "rate_limit", ["uuid"], unique=True)
    op.create_index("ix_rate_limit_identifier", "rate_limit", ["identifier"])


def downgrade():
    op.drop_table("rate_limit")
    op.drop_table("auth_token")
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("email")
