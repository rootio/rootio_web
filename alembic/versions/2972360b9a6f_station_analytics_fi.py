"""station_analytics_fields

Revision ID: 2972360b9a6f
Revises: 4d15178b2ddf
Create Date: 2014-04-27 11:40:27.502517

"""

# revision identifiers, used by Alembic.
revision = '2972360b9a6f'
down_revision = '4d15178b2ddf'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.add_column('radio_stationanalytic', sa.Column('gps_lat', sa.Float(), nullable=True))
    op.add_column('radio_stationanalytic', sa.Column('gps_lon', sa.Float(), nullable=True))
    op.add_column('radio_stationanalytic', sa.Column('gsm_signal', sa.Float(), nullable=True))
    op.add_column('radio_stationanalytic', sa.Column('wifi_connected', sa.Boolean(), nullable=True))
    op.drop_column('radio_stationanalytic', u'gsm_connectivity')


def downgrade():
    op.add_column('radio_stationanalytic', sa.Column(u'gsm_connectivity', postgresql.DOUBLE_PRECISION(precision=53), nullable=True))
    op.drop_column('radio_stationanalytic', 'wifi_connected')
    op.drop_column('radio_stationanalytic', 'gsm_signal')
    op.drop_column('radio_stationanalytic', 'gps_lon')
    op.drop_column('radio_stationanalytic', 'gps_lat')
