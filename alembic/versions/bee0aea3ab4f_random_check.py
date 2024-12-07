"""random check

Revision ID: bee0aea3ab4f
Revises: 53b9fd59409c
Create Date: 2024-12-04 02:43:21.707908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bee0aea3ab4f'
down_revision: Union[str, None] = '53b9fd59409c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
