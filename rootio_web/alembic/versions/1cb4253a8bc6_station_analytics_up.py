"""station_analytics_update

Revision ID: 1cb4253a8bc6
Revises: 2972360b9a6f
Create Date: 2014-04-27 13:01:26.309272

"""

# revision identifiers, used by Alembic.
revision = '1cb4253a8bc6'
down_revision = '2972360b9a6f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('radio_station', sa.Column('analytic_update_frequency', sa.Float(), nullable=True))


def downgrade():
    op.drop_column('radio_station', 'analytic_update_frequency')
