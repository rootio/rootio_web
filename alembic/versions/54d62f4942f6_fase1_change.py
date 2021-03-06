"""fase1_change

Revision ID: 54d62f4942f6
Revises: 592ac1a4ca88
Create Date: 2016-09-01 16:57:21.382116

"""

# revision identifiers, used by Alembic.
revision = '54d62f4942f6'
down_revision = '592ac1a4ca88'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(u'radio_contenttype',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    #op.drop_table(u'radio_content_type')
    op.drop_column(u'content_track', u'content_id')
    op.drop_column(u'content_track', u'uploaded_by')
    op.drop_column(u'content_track', u'description')
    op.drop_column(u'content_track', u'name')
    op.drop_column(u'content_uploads', u'title')
    op.drop_column(u'content_uploads', u'track_id')
    op.drop_column(u'content_uploads', u'uri')
    op.drop_column(u'content_uploads', u'uploaded_by')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'content_uploads', sa.Column(u'uploaded_by', sa.INTEGER(), nullable=True))
    op.add_column(u'content_uploads', sa.Column(u'uri', sa.VARCHAR(length=200), nullable=True))
    op.add_column(u'content_uploads', sa.Column(u'track_id', sa.INTEGER(), nullable=True))
    op.add_column(u'content_uploads', sa.Column(u'title', sa.VARCHAR(length=100), nullable=True))
    op.add_column(u'content_track', sa.Column(u'name', sa.VARCHAR(length=100), nullable=True))
    op.add_column(u'content_track', sa.Column(u'description', sa.TEXT(), nullable=True))
    op.add_column(u'content_track', sa.Column(u'uploaded_by', sa.INTEGER(), nullable=True))
    op.add_column(u'content_track', sa.Column(u'content_id', sa.INTEGER(), nullable=True))
    op.create_table(u'radio_content_type',
    sa.Column(u'created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column(u'updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column(u'id', sa.INTEGER(), server_default="nextval('radio_content_type_id_seq'::regclass)", nullable=False),
    sa.Column(u'name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column(u'description', sa.TEXT(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint(u'id', name=u'radio_content_type_pkey')
    )
    op.drop_table(u'radio_contenttype')
    ### end Alembic commands ###
