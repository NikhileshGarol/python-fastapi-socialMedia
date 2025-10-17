"""add sentiment,summary fields to posts table

Revision ID: 59ed098d126e
Revises: 6d33eb574dee
Create Date: 2025-10-01 10:41:39.963451

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59ed098d126e'
down_revision: Union[str, Sequence[str], None] = '6d33eb574dee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('sentiment', sa.String(50),
                  nullable=False, server_default='NEUTRAL'))
    op.add_column('posts', sa.Column('summary', sa.String(300), nullable=True))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'sentiment')
    op.drop_column('posts', 'summary')
    pass
