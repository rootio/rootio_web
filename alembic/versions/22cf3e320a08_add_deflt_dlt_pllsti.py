"""add_deflt_dlt_pllstitm

Revision ID: 22cf3e320a08
Revises: f75b5dfaf06
Create Date: 2016-11-29 18:54:13.898568

"""

# revision identifiers, used by Alembic.
revision = '22cf3e320a08'
down_revision = 'f75b5dfaf06'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('content_musicplaylistitem', sa.Column('deleted', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('content_musicplaylistitem', 'deleted')
    ### end Alembic commands ###
