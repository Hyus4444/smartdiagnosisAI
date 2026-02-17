"""add created_by to patients

Revision ID: 3d3864697a1a
Revises: 3d0ee7f48df9
Create Date: 2026-02-17 14:48:46.331592

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '3d3864697a1a'
down_revision: Union[str, Sequence[str], None] = '3d0ee7f48df9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "clinical_records",
        sa.Column("created_by", UUID(as_uuid=True), nullable=False),
    )
    op.create_foreign_key(
        "fk_clinical_records_created_by_users",
        "clinical_records",
        "users",
        ["created_by"],
        ["id"],
    )



def downgrade() -> None:
    """Downgrade schema."""
    pass
