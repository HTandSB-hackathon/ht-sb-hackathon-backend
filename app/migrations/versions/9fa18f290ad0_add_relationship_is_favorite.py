"""add relationship is favorite

Revision ID: 9fa18f290ad0
Revises: 2f78bffa2892
Create Date: 2025-06-03 09:29:46.582740

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9fa18f290ad0'
down_revision: Union[str, None] = '2f78bffa2892'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('relationships', sa.Column('is_favorite', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('relationships', 'is_favorite')
    # ### end Alembic commands ###
