"""Add foreign key constraint for TTS language

Revision ID: 2970098205c8
Revises: 180f69d36c8d
Create Date: 2018-09-24 23:49:50.050750

"""

# revision identifiers, used by Alembic.
revision = '2970098205c8'
down_revision = '180f69d36c8d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('radio_station_tts_language_fk', 'radio_station', 'radio_language', ['tts_language_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('radio_station_tts_language_fk', 'radio_station', type_='foreignkey')
    ### end Alembic commands ###