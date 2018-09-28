"""make sqlalchemy datetime columns timezone aware
requires deleting fields with default values (created_time)
will recreate with next migration

effects:
ScheduledProgram.start
ScheduledProgram.end

ScheduledBlock.start_time
ScheduledBlock.end_time

delete existing fields with default values
Episode.created_time
Recording.created_time
StationAnalytic.created_time
OnAirProgram.created_time

Revision ID: 16980fb44a9c
Revises: ad55d401537
Create Date: 2014-03-12 16:04:38.669445

"""

# revision identifiers, used by Alembic.
revision = '16980fb44a9c'
down_revision = 'ad55d401537'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column(
        table_name = 'radio_scheduledprogram',
        column_name = 'start',
        nullable = False,
        type_ = sa.types.DateTime(timezone=True),
    )
    op.alter_column(
        table_name = 'radio_scheduledprogram',
        column_name = 'end',
        nullable = False,
        type_ = sa.types.DateTime(timezone=True),
    )

    op.alter_column(
        table_name = 'radio_scheduledblock',
        column_name = 'start_time',
        nullable = False,
        type_ = sa.types.Time(timezone=True),
    )
    op.alter_column(
        table_name = 'radio_scheduledblock',
        column_name = 'end_time',
        nullable = False,
        type_ = sa.types.Time(timezone=True),
    )

    op.drop_column('radio_episode','created_time')
    op.drop_column('radio_recording','created_time')
    op.drop_column('radio_stationanalytic','created_time')
    op.drop_column('onair_program','created_time')

def downgrade():
    pass