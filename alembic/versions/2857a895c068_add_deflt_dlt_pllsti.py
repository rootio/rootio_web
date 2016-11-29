"""add_deflt_dlt_pllstitm

Revision ID: 2857a895c068
Revises: 2485aab44d4d
Create Date: 2016-11-29 18:52:18.232985

"""

# revision identifiers, used by Alembic.
revision = '2857a895c068'
down_revision = '2485aab44d4d'

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