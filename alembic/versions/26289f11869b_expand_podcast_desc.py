"""expand_podcast_desc

Revision ID: 26289f11869b
Revises: 26eb16c4aeaf
Create Date: 2017-08-16 23:49:18.869515

"""

# revision identifiers, used by Alembic.
revision = '26289f11869b'
down_revision = '26eb16c4aeaf'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table(u'radio_content_type')
    op.alter_column(u'content_podcast', 'description',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=1000),
               existing_nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(u'content_podcast', 'description',
               existing_type=sa.String(length=1000),
               type_=sa.VARCHAR(length=100),
               existing_nullable=True)
    op.create_table(u'radio_content_type',
    sa.Column(u'created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column(u'updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column(u'id', sa.INTEGER(), server_default="nextval('radio_content_type_id_seq'::regclass)", nullable=False),
    sa.Column(u'name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column(u'description', sa.TEXT(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint(u'id', name=u'radio_content_type_pkey')
    )
    ### end Alembic commands ###
