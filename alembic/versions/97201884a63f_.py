"""empty message

Revision ID: 97201884a63f
Revises: 
Create Date: 2024-10-22 02:21:58.422031

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '97201884a63f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('song_artist', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('song_title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('song_url', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('screenshot_url', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###
