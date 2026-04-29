"""add missing defaults to url mappings

Revision ID: e9fac901e696
Revises: d073ea08b8c7
Create Date: 2026-04-29 15:23:15.437192

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e9fac901e696"
down_revision = "d073ea08b8c7"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "url_mappings",
        "created_at",
        server_default=sa.text("now()"),
        existing_nullable=False,
    )
    op.alter_column(
        "url_mappings",
        "updated_at",
        server_default=sa.text("now()"),
        existing_nullable=False,
    )
    op.alter_column(
        "url_mappings",
        "access_count",
        server_default=sa.text("0"),
        existing_nullable=False,
    )


def downgrade():
    op.alter_column(
        "url_mappings",
        "created_at",
        server_default=None,
        existing_nullable=False,
    )
    op.alter_column(
        "url_mappings",
        "updated_at",
        server_default=None,
        existing_nullable=False,
    )
    op.alter_column(
        "url_mappings",
        "access_count",
        server_default=None,
        existing_nullable=False,
    )
