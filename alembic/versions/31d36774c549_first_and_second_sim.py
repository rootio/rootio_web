"""split gsm signal in two analytics, one per sim card

Revision ID: 31d36774c549
Revises: 528f90a47515
Create Date: 2019-01-23 15:16:58.514742

"""

# revision identifiers, used by Alembic.
revision = '31d36774c549'
down_revision = '528f90a47515'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('radio_stationanalytic', 'gsm_signal', new_column_name='gsm_signal_1')
    op.add_column('radio_stationanalytic', sa.Column('gsm_signal_2', sa.Integer(), nullable=True))


def downgrade():
    op.alter_column('radio_stationanalytic', 'gsm_signal_1', new_column_name='gsm_signal')
    op.drop_column('radio_stationanalytic', 'gsm_signal_2')
