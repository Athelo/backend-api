"""user_model_birthday

Revision ID: ebaf5e58f37a
Revises: c6397f0cef4d
Create Date: 2024-01-08 23:06:01.195269

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ebaf5e58f37a'
down_revision = 'c6397f0cef4d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('profiles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('birthday', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('phone', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('profiles', schema=None) as batch_op:
        batch_op.drop_column('phone')
        batch_op.drop_column('birthday')

    # ### end Alembic commands ###
