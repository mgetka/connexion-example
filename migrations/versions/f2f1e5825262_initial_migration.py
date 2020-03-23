"""Initial migration

Revision ID: f2f1e5825262
Revises: mgetka
Create Date: 2020-03-23 13:15:04.728156+00:00

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "f2f1e5825262"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column(
            "created",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "modified",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_entries_name"), "entries", ["name"], unique=True)


def downgrade():
    op.drop_index(op.f("ix_entries_name"), table_name="entries")
    op.drop_table("entries")
