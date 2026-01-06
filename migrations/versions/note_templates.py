"""Add daily_template and note_template columns to user table

Revision ID: note_templates_001
Revises: email_auth_tokens_001
Create Date: 2026-01-06 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "note_templates_001"
down_revision = "email_auth_tokens_001"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("daily_template", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("note_template", sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("note_template")
        batch_op.drop_column("daily_template")
