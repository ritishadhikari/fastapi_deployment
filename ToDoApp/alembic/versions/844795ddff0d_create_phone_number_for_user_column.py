"""Create Phone Number for user column

Revision ID: 844795ddff0d
Revises: 
Create Date: 2025-06-01 09:48:46.475171

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '844795ddff0d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(table_name="users",
                  column=sa.Column(
                      "phone_number",
                      sa.String(),
                      nullable=True)
                  )


def downgrade() -> None:
    """Downgrade schema."""
    pass
