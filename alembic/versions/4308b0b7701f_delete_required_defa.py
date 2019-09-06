"""delete required,default to null on community_menu

Revision ID: 4308b0b7701f
Revises: 3fd0a7ee1e16
Create Date: 2019-09-01 18:47:13.540634

"""

# revision identifiers, used by Alembic.
revision = '4308b0b7701f'
down_revision = '3fd0a7ee1e16'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table


def upgrade():
    op.drop_column('content_communitymenu', 'deleted')

    op.add_column(
        'content_communitymenu',
        sa.Column('deleted',
                  sa.Boolean(),
                  nullable=False,
                  server_default=sa.false()))

    old_timers = table(
        'content_communitymenu',
        sa.Column('deleted', sa.Boolean())
        # Other columns not needed for the data migration
    )


def downgrade():
    pass
