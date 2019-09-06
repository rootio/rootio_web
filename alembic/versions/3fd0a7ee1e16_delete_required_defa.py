"""delete required,default to null on voiceprompt

Revision ID: 3fd0a7ee1e16
Revises: 5936ede3879d
Create Date: 2019-09-01 16:10:30.403953

"""

# revision identifiers, used by Alembic.
revision = '3fd0a7ee1e16'
down_revision = '5936ede3879d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table


def upgrade():
    op.drop_column('configuration_voiceprompt', 'deleted')

    op.add_column(
        'configuration_voiceprompt',
        sa.Column('deleted',
                  sa.Boolean(),
                  nullable=False,
                  server_default=sa.false()))

    old_timers = table(
        'configuration_voiceprompt',
        sa.Column('deleted', sa.Boolean())
        # Other columns not needed for the data migration
    )


def downgrade():
    pass