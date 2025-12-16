"""Add week_start_monday column to User table

Revision ID: week_start_monday_001
Revises: f1803e0263f1
Create Date: 2025-12-12 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "week_start_monday_001"
down_revision = "f1803e0263f1"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "week_start_monday", sa.Boolean(), nullable=True, server_default="0"
            )
        )


def downgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("week_start_monday")
