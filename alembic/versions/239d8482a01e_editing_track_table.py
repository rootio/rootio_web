"""editing track table

Revision ID: 239d8482a01e
Revises: 285ff6ea690b
Create Date: 2016-09-28 16:39:18.193278

"""

# revision identifiers, used by Alembic.
revision = '239d8482a01e'
down_revision = '285ff6ea690b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'content_track', sa.Column('type_id', sa.Integer(), nullable=True))
    op.drop_column(u'content_track', u'content_contenttypeid')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'content_track', sa.Column(u'content_contenttypeid', sa.INTEGER(), nullable=True))
    op.drop_column(u'content_track', 'type_id')
    ### end Alembic commands ###
