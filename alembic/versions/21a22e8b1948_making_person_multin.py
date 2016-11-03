"""making_person_multinetwork

Revision ID: 21a22e8b1948
Revises: 58dfdfe8ae74
Create Date: 2016-10-31 19:16:19.270884

"""

# revision identifiers, used by Alembic.
revision = '21a22e8b1948'
down_revision = '58dfdfe8ae74'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('radio_personnetwork',
    sa.Column('network_id', sa.Integer(), nullable=True),
    sa.Column('person_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['network_id'], ['radio_network.id'], ),
    sa.ForeignKeyConstraint(['person_id'], ['radio_person.id'], ),
    sa.PrimaryKeyConstraint()
    )
    op.drop_column(u'radio_person', 'network_id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'radio_person', sa.Column('network_id', sa.INTEGER(), nullable=True))
    op.drop_table('radio_personnetwork')
    ### end Alembic commands ###