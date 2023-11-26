"""create address table

Revision ID: 9fc4f0d94210
Revises: cff4cdfa5152
Create Date: 2023-11-19 10:52:00.746611

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9fc4f0d94210'
down_revision: Union[str, None] = 'cff4cdfa5152'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('address',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('address1', sa.String(), nullable=False),
                    sa.Column('address2', sa.String(), nullable=False),
                    sa.Column('city', sa.String(), nullable=False),
                    sa.Column('state', sa.String(), nullable=False),
                    sa.Column('country', sa.String(), nullable=False),
                    sa.Column('postalcode', sa.String(), nullable=False)
                    )


def downgrade() -> None:
    op.drop_table('address')
