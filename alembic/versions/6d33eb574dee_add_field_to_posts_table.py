"""add field to posts table

Revision ID: 6d33eb574dee
Revises: 
Create Date: 2025-09-30 13:03:55.727958

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6d33eb574dee'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column(
        'description', sa.String(255), nullable=True))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'description')
    pass
