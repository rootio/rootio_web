"""add_uploads

Revision ID: 9dfe6c16692
Revises: 2726a547193b
Create Date: 2016-08-31 13:11:43.695129

"""

# revision identifiers, used by Alembic.
revision = '9dfe6c16692'
down_revision = '2726a547193b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(u'content_uploads',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=True),
    sa.Column('uri', sa.String(length=200), nullable=True),
    sa.Column('uploaded_by', sa.Integer(), nullable=True),
    sa.Column('track_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['track_id'], ['content_track.id'], ),
    sa.ForeignKeyConstraint(['uploaded_by'], ['user_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table(u'content_uploads')
    ### end Alembic commands ###
