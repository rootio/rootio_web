"""jsontype

Revision ID: 54068667be18
Revises: 33313179882b
Create Date: 2014-04-30 12:01:38.148725

"""

# revision identifiers, used by Alembic.
revision = '54068667be18'
down_revision = '33313179882b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():

    # first create with nullable=True
    op.alter_column(u'radio_programtype', 'definition',
               existing_type=postgresql.BYTEA(),
               nullable=True)
    op.alter_column(u'radio_programtype', 'phone_functions',
               existing_type=postgresql.BYTEA(),
               nullable=True)

    #fill with empty string
    for col in ['definition','phone_functions']:
        field = sa.sql.table('radio_programtype', sa.sql.column(col))
        op.execute(field.update(values={col:''}))


    #and set nullable=False
    op.alter_column(u'radio_programtype', 'definition',
               existing_type=postgresql.BYTEA(),
               nullable=False)
    op.alter_column(u'radio_programtype', 'phone_functions',
               existing_type=postgresql.BYTEA(),
               nullable=False)


def downgrade():
        op.alter_column(u'radio_programtype', 'definition',
               existing_type=postgresql.BYTEA(),
               nullable=True)
        op.alter_column(u'radio_programtype', 'phone_functions',
               existing_type=postgresql.BYTEA(),
               nullable=True)
