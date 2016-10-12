"""timestamp_mixins

Revision ID: 27fab241689c
Revises: 16980fb44a9c
Create Date: 2014-03-12 16:25:33.536961

"""

# revision identifiers, used by Alembic.
revision = '27fab241689c'
down_revision = '16980fb44a9c'

from alembic import op
import sqlalchemy as sa

import datetime

def upgrade():
    table_names = [ 'onair_program',
                    'radio_episode',
                    'radio_language',
                    'radio_location',
                    'radio_network',
                    'radio_paddingcontent',
                    'radio_person',
                    'radio_program',
                    'radio_programtype',
                    'radio_recording',
                    'radio_role',
                    'radio_scheduledblock',
                    'radio_scheduledprogram',
                    'radio_station',
                    'radio_stationanalytic']


    #first create columns with nullable=True
    for table_name in table_names:
        op.add_column(table_name, sa.Column('created_at', type_=sa.DateTime(timezone=True), nullable=True))
        op.add_column(table_name, sa.Column('updated_at', type_=sa.DateTime(timezone=True), nullable=True))

    #then set times to now
    now = datetime.datetime.utcnow()
    for table_name in table_names:
        created_at = sa.sql.table(table_name, sa.sql.column('created_at'))
        op.execute(created_at.update().values(created_at=now))

        updated_at = sa.sql.table(table_name, sa.sql.column('updated_at'))
        op.execute(updated_at.update().values(updated_at=now))

    #then set back to nullable=False
    for table_name in table_names:
        op.alter_column(table_name, 'created_at', nullable=False)
        op.alter_column(table_name, 'updated_at', nullable=False)

def downgrade():
    #there is no backspace
    pass