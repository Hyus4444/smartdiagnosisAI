"""add created_by to patients

Revision ID: 3d0ee7f48df9
Revises: 756fdf2e2195
Create Date: 2026-02-10 18:01:40.529754

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "3d0ee7f48df9"
down_revision: Union[str, Sequence[str], None] = "756fdf2e2195"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Agregar columna created_by NOT NULL
    op.add_column(
        "patients",
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            nullable=False
        ),
    )

    # 2. Crear índice para scoping por usuario
    op.create_index(
        "ix_patients_created_by",
        "patients",
        ["created_by"]
    )

    # 3. Crear Foreign Key contra users.id
    op.create_foreign_key(
        "fk_patients_created_by_users",
        source_table="patients",
        referent_table="users",
        local_cols=["created_by"],
        remote_cols=["id"],
        ondelete="RESTRICT"
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_patients_created_by_users",
        "patients",
        type_="foreignkey"
    )

    op.drop_index(
        "ix_patients_created_by",
        table_name="patients"
    )

    op.drop_column(
        "patients",
        "created_by"
    )
