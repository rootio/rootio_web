"""make telephony_phonenumber raw_number nullable True

Revision ID: dc611df9442
Revises: initial
Create Date: 2013-10-25 18:15:47.156128

"""

# revision identifiers, used by Alembic.
revision = 'dc611df9442'
down_revision = 'initial'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column("telephony_phonenumber", "raw_number", nullable=True)


def downgrade():
    op.alter_column("telephony_phonenumber", "raw_number", nullable=False)
