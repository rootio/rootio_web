"""media available for scheduledProgram

Revision ID: 1e5d7bf69e43
Revises: 1df4326b5214
Create Date: 2019-09-22 14:49:16.800374

"""

# revision identifiers, used by Alembic.
revision = '1e5d7bf69e43'
down_revision = '7ce753c2606'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.add_column('radio_scheduledprogram', sa.Column('media_available', sa.Boolean(), nullable=True))

def downgrade():
    op.drop_column('radio_scheduledprogram', 'media_available')