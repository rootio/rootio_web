""" new fields for station model

Revision ID: 6722b0ef4e1
Revises: 276473e97ac
Create Date: 2014-04-01 17:11:58.922037

"""

# revision identifiers, used by Alembic.
revision = '6722b0ef4e1'
down_revision = '276473e97ac'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('radio_station', sa.Column('broadcast_ip', sa.String(length=16), nullable=True))
    op.add_column('radio_station', sa.Column('client_update_frequency', sa.Float(), nullable=True))


def downgrade():
    op.drop_column('radio_station', 'client_update_frequency')
    op.drop_column('radio_station', 'broadcast_ip')
