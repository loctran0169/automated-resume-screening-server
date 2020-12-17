"""updateJobPostModel

Revision ID: 5facbee86f37
Revises: 15caaee8299b
Create Date: 2020-12-18 00:09:55.607165

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5facbee86f37'
down_revision = '15caaee8299b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('job_posts', 'benefit_text',
               existing_type=mysql.TEXT(collation='utf8_unicode_ci'),
               nullable=False)
    op.alter_column('job_posts', 'description_text',
               existing_type=mysql.TEXT(collation='utf8_unicode_ci'),
               nullable=False)
    op.alter_column('job_posts', 'requirement_text',
               existing_type=mysql.TEXT(collation='utf8_unicode_ci'),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('job_posts', 'requirement_text',
               existing_type=mysql.TEXT(collation='utf8_unicode_ci'),
               nullable=True)
    op.alter_column('job_posts', 'description_text',
               existing_type=mysql.TEXT(collation='utf8_unicode_ci'),
               nullable=True)
    op.alter_column('job_posts', 'benefit_text',
               existing_type=mysql.TEXT(collation='utf8_unicode_ci'),
               nullable=True)
    # ### end Alembic commands ###
