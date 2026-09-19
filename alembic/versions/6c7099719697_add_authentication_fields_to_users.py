"""add authentication fields to users

Revision ID: 6c7099719697
Revises: 72e149ec1cce
Create Date: 2026-09-18 20:06:09.402030

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c7099719697'
down_revision: Union[str, Sequence[str], None] = '72e149ec1cce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Crear primero el campo opcional para conservar los usuarios ya existentes.
    op.add_column(
        "users",
        sa.Column("hashed_password", sa.String(), nullable=True),
    )
    op.execute("UPDATE users SET hashed_password = '' WHERE hashed_password IS NULL")

    # Dejar el campo obligatorio después de completar los registros anteriores.
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "hashed_password",
            existing_type=sa.String(),
            nullable=False,
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("hashed_password")
