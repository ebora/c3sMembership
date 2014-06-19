"""AfMs: add token and date to AfM for email address confirmation

Revision ID: 4e3db989103f
Revises: 4ea1ace107fa
Create Date: 2014-06-13 02:09:45.366288

"""

# revision identifiers, used by Alembic.
revision = '4e3db989103f'
down_revision = '4ea1ace107fa'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('members', sa.Column('email_confirm_token', sa.Unicode(length=255), nullable=True))
    op.add_column('members', sa.Column('email_confirm_mail_date', sa.DateTime(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('members', 'email_confirm_token')
    op.drop_column('members', 'email_confirm_mail_date')
    ### end Alembic commands ###
