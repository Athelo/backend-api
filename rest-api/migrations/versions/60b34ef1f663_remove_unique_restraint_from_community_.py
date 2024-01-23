"""remove unique restraint from community thread owner

Revision ID: 60b34ef1f663
Revises: cde197eab9ac
Create Date: 2024-01-23 15:14:28.398880

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "60b34ef1f663"
down_revision = "cde197eab9ac"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("community_threads", schema=None) as batch_op:
        batch_op.drop_constraint("uq_community_threads_owner_id", type_="unique")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table("community_threads", schema=None) as batch_op:
        batch_op.create_unique_constraint("uq_community_threads_owner_id", ["owner_id"])

    # ### end Alembic commands ###
