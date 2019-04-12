"""add station events

Revision ID: 269008ea89b6
Revises: 62b8dd615a3
Create Date: 2019-04-04 10:28:40.450558

"""

# revision identifiers, used by Alembic.
revision = '269008ea89b6'
down_revision = '62b8dd615a3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('radio_stationevent',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('category', sa.String(length=100), nullable=False),
    sa.Column('action', sa.String(length=100), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('radio_stationevent')
