"""Configurable looping content

Revision ID: 530870fbb266
Revises: fff564ee60b
Create Date: 2019-08-02 13:02:27.775358

"""

# revision identifiers, used by Alembic.
revision = '530870fbb266'
down_revision = 'fff564ee60b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('radio_station', sa.Column('loop_ads', sa.Integer(), nullable=True))
    op.add_column('radio_station', sa.Column('loop_announcements', sa.Integer(), nullable=True))
    op.add_column('radio_station', sa.Column('loop_greetings', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('radio_station', 'loop_greetings')
    op.drop_column('radio_station', 'loop_announcements')
    op.drop_column('radio_station', 'loop_ads')
    ### end Alembic commands ###
