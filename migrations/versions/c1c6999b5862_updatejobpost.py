"""updateJobPost

Revision ID: c1c6999b5862
Revises: 15d9edaece0d
Create Date: 2020-12-20 03:54:13.704411

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1c6999b5862'
down_revision = '15d9edaece0d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('job_posts', sa.Column('total_applies', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('job_posts', 'total_applies')
    # ### end Alembic commands ###
