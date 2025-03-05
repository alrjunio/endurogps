"""Migraçao Inicial

Revision ID: ad05f0c6b38e
Revises: f3d1c0f6b138
Create Date: 2025-03-05 17:30:53.201922

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad05f0c6b38e'
down_revision: Union[str, None] = 'f3d1c0f6b138'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
