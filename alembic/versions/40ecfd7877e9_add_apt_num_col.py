"""add apt num col

Revision ID: 40ecfd7877e9
Revises: 6266855bba66
Create Date: 2023-11-19 15:08:55.123186

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40ecfd7877e9'
down_revision: Union[str, None] = '6266855bba66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('address', sa.Column('apt_num', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('address', 'apt_num')
