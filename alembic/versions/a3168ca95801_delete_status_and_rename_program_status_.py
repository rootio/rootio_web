"""delete status and rename program_status to status

Revision ID: a3168ca95801
Revises: 7ce753c2606
Create Date: 2019-09-24 08:36:27.300413

"""

# revision identifiers, used by Alembic.
revision = 'a3168ca95801'
down_revision = '7ce753c2606'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.drop_column('radio_scheduledprogram','status')
    op.alter_column('radio_scheduledprogram', 'program_status',
               new_column_name='status', existing_nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    ''
    ### end Alembic commands ###