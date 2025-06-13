"""Create Address for user column

Revision ID: 13f3ed091e0f
Revises: 844795ddff0d
Create Date: 2025-06-01 10:28:14.093021

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '13f3ed091e0f'
down_revision: Union[str, None] = '844795ddff0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(table_name="users",
                  column=sa.Column(
                      "address",
                      sa.String(),
                      nullable=True)
                  )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(table_name="users",column_name="address")
