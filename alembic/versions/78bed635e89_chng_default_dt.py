"""chng_default_dt

Revision ID: 78bed635e89
Revises: 16742620dda5
Create Date: 2017-08-23 15:35:09.277292

"""

# revision identifiers, used by Alembic.
revision = '78bed635e89'
down_revision = '16742620dda5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'content_podcast', sa.Column('date_created', sa.DateTime(timezone=True), server_default=func.now(), nullable=True))
    op.alter_column(u'content_podcast', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default="2017-01-11 21:14:53.469648+00'::timestamp with time zone")
    op.add_column(u'content_podcastdownload', sa.Column('date_created', sa.DateTime(timezone=True), nullable=True))
    op.add_column(u'content_podcastdownload', sa.Column('date_downloaded', sa.DateTime(timezone=True), server_default=func.now(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'content_podcastdownload', 'date_downloaded')
    op.drop_column(u'content_podcastdownload', 'date_created')
    op.alter_column(u'content_podcast', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default="2017-01-11 21:14:53.469648+00'::timestamp with time zone")
    op.drop_column(u'content_podcast', 'date_created')
    ### end Alembic commands ###
