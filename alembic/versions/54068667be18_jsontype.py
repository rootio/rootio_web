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
    # op.add_column('radio_programtype', sa.Column('definition', sa.PickleType(), nullable=True))
    # op.add_column('radio_programtype', sa.Column('phone_functions', sa.PickleType(), nullable=True))

    #clear existing values
    for col in ['definition','phone_functions']:
        field = sa.sql.table('radio_programtype', sa.sql.column(col))
        op.execute(field.update(values={col:''}))

    #convert to text
    op.alter_column(u'radio_programtype', 'definition',
               type_=sa.Text(),
               existing_type=sa.PickleType(),
               nullable=False)
    op.alter_column(u'radio_programtype', 'phone_functions',
               type_=sa.Text(),
               existing_type=sa.PickleType(),
               nullable=False)

def downgrade():
    op.drop_column('radio_programtype', 'definition')
    op.drop_column('radio_programtype', 'phone_functions')