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

def upgrade():
    # op.add_column(u'radio_programtype', sa.Column('definition', sa.Text(), nullable=True))
    op.add_column(u'radio_programtype', sa.Column('phone_functions', sa.Text(), nullable=True))

    #fill with empty string
    for col in ['definition','phone_functions']:
        field = sa.sql.table('radio_programtype', sa.sql.column(col))
        op.execute(field.update(values={col:''}))

def downgrade():
    op.drop_column('radio_programtype', 'definition')
    op.drop_column('radio_programtype', 'phone_functions')