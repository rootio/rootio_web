"""Add TTS configuration to station

Revision ID: 180f69d36c8d
Revises: be876afb3eb1
Create Date: 2018-09-21 10:10:59.130732

"""

# revision identifiers, used by Alembic.
revision = '180f69d36c8d'
down_revision = 'be876afb3eb1'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('radio_station', sa.Column('tts_gender', sa.String(length=100), nullable=True))
    op.add_column('radio_station', sa.Column('tts_accent', sa.String(length=100), nullable=True))
    op.add_column('radio_station', sa.Column('tts_audio_format', sa.String(length=100), nullable=True))
    op.add_column('radio_station', sa.Column('tts_sample_rate', sa.String(length=100), nullable=True))
    op.add_column('radio_station', sa.Column('tts_language_id', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('radio_station', 'tts_language_id')
    op.drop_column('radio_station', 'tts_sample_rate')
    op.drop_column('radio_station', 'tts_audio_format')
    op.drop_column('radio_station', 'tts_accent')
    op.drop_column('radio_station', 'tts_gender')
    ### end Alembic commands ###