"""add_track

Revision ID: 2726a547193b
Revises: 47639c53cc4e
Create Date: 2016-08-31 10:43:04.021255

"""

# revision identifiers, used by Alembic.
revision = '2726a547193b'
down_revision = '47639c53cc4e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(u'radio_content_type',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table(u'content_track',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('content_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['content_id'], ['radio_content_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table(u'radio_contenttype')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(u'radio_contenttype',
    sa.Column(u'created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column(u'updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column(u'id', sa.INTEGER(), server_default="nextval('radio_contenttype_id_seq'::regclass)", nullable=False),
    sa.Column(u'name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column(u'description', sa.TEXT(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint(u'id', name=u'radio_contenttype_pkey')
    )
    op.drop_table(u'content_track')
    op.drop_table(u'radio_content_type')
    ### end Alembic commands ###
