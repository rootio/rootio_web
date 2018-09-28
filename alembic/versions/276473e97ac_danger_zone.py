""" Don't store timezone on time-only objects. It doesn't make sense with DST.
Assume time is always local.

Revision ID: 276473e97ac
Revises: 1ba2e0725603
Create Date: 2014-03-13 17:18:02.424697

"""

# revision identifiers, used by Alembic.
revision = '276473e97ac'
down_revision = '1ba2e0725603'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column(
        table_name = 'radio_scheduledblock',
        column_name = 'start_time',
        nullable = False,
        type_ = sa.types.Time(timezone=False),
    )
    op.alter_column(
        table_name = 'radio_scheduledblock',
        column_name = 'end_time',
        nullable = False,
        type_ = sa.types.Time(timezone=False),
    )


def downgrade():
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
