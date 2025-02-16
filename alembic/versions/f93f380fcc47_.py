"""empty message

Revision ID: f93f380fcc47
Revises: 
Create Date: 2024-07-19 11:48:02.396096

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f93f380fcc47'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('track_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('chat_id', sa.Integer(), nullable=False),
    sa.Column('crypto_name', sa.String(), nullable=False),
    sa.Column('min_threshold', sa.Float(), nullable=False),
    sa.Column('max_threshold', sa.Float(), nullable=False),
    sa.Column('min_notified', sa.Boolean(), nullable=True),
    sa.Column('max_notified', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('track_info')
    # ### end Alembic commands ###
