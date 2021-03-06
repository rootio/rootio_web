"""gateway_m2m

Revision ID: 5769f7c6759c
Revises: 13b2e84fd798
Create Date: 2014-04-28 22:50:14.401843

"""

# revision identifiers, used by Alembic.
revision = '5769f7c6759c'
down_revision = '13b2e84fd798'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(u'radio_incominggateway',
    sa.Column(u'incominggateway_id', sa.Integer(), nullable=True),
    sa.Column(u'station_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['incominggateway_id'], ['telephony_gateway.id'], ),
    sa.ForeignKeyConstraint(['station_id'], ['radio_station.id'], ),
    sa.PrimaryKeyConstraint()
    )
    op.create_table(u'radio_outgoinggateway',
    sa.Column(u'outgoinggateway_id', sa.Integer(), nullable=True),
    sa.Column(u'station_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['outgoinggateway_id'], ['telephony_gateway.id'], ),
    sa.ForeignKeyConstraint(['station_id'], ['radio_station.id'], ),
    sa.PrimaryKeyConstraint()
    )
    op.drop_column(u'radio_station', u'gateway_id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'radio_station', sa.Column(u'gateway_id', sa.INTEGER(), nullable=True))
    op.drop_table(u'radio_outgoinggateway')
    op.drop_table(u'radio_incominggateway')
    ### end Alembic commands ###
