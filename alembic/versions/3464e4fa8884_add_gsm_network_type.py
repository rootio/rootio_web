"""add gsm network type

Revision ID: 3464e4fa8884
Revises: 31d36774c549
Create Date: 2019-01-23 15:27:09.901738

"""

# revision identifiers, used by Alembic.
revision = '3464e4fa8884'
down_revision = '31d36774c549'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('radio_stationanalytic', sa.Column('gsm_network_type_1', sa.String(length=30), nullable=True))
    op.add_column('radio_stationanalytic', sa.Column('gsm_network_type_2', sa.String(length=30), nullable=True))


def downgrade():
    op.drop_column('radio_stationanalytic', 'gsm_network_type_2')
    op.drop_column('radio_stationanalytic', 'gsm_network_type_1')
