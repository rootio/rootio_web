""" rename ScheduledProgram.episode_id ScheduledProgram.program_id

Revision ID: 3db20d7c744c
Revises: 42623b4e4a62
Create Date: 2013-10-28 11:21:45.447212

"""

# revision identifiers, used by Alembic.
revision = '3db20d7c744c'
down_revision = '42623b4e4a62'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column(u'radio_scheduledprogram', 'episode_id', new_column_name='program_id')

def downgrade():
    op.alter_column(u'radio_scheduledprogram', 'program_id', new_column_name='episode_id')