"""AddNewTablesForSaveFeaturesUpdate

Revision ID: 24ecd7326544
Revises: 7b4e03ff2c23
Create Date: 2021-01-02 16:50:38.934762

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '24ecd7326544'
down_revision = '7b4e03ff2c23'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('recruiter_resume_saves', sa.Column('resume_id', sa.Integer(), nullable=False))
    op.drop_constraint('recruiter_resume_saves_ibfk_1', 'recruiter_resume_saves', type_='foreignkey')
    op.create_foreign_key(None, 'recruiter_resume_saves', 'resumes', ['resume_id'], ['id'])
    op.drop_column('recruiter_resume_saves', 'job_post_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('recruiter_resume_saves', sa.Column('job_post_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'recruiter_resume_saves', type_='foreignkey')
    op.create_foreign_key('recruiter_resume_saves_ibfk_1', 'recruiter_resume_saves', 'job_posts', ['job_post_id'], ['id'])
    op.drop_column('recruiter_resume_saves', 'resume_id')
    # ### end Alembic commands ###
