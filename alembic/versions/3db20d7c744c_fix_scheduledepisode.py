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
    op.add_column('radio_scheduledprogram',
        sa.Column('program_id', sa.INTEGER, sa.ForeignKey('radio_program.id'))
    )
    op.drop_column('radio_scheduledprogram','episode_id')

def downgrade():
    op.add_column('radio_scheduledprogram',
        sa.Column('episode_id', sa.INTEGER, sa.ForeignKey('radio_episode.id'))
    )
    op.drop_column('radio_scheduledprogram','program_id')