"""Migration-add-idm

Revision ID: 248f76f12a5d
Revises: 3b362bbb9d04
Create Date: 2020-12-07 14:12:56.803728

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '248f76f12a5d'
down_revision = '3b362bbb9d04'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('candidate', sa.Column('idm', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('candidate', 'idm')
    # ### end Alembic commands ###
