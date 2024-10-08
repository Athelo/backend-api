"""add chat room identifier to thread

Revision ID: cde197eab9ac
Revises: ce91d646c914
Create Date: 2024-01-23 14:00:15.420578

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "cde197eab9ac"
down_revision = "ce91d646c914"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("community_threads", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "chat_room_id",
                sa.UUID(),
                server_default=sa.text("gen_random_uuid()"),
                nullable=False,
            )
        )
        batch_op.create_index(
            batch_op.f("ix_community_threads_chat_room_id"),
            ["chat_room_id"],
            unique=True,
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table("community_threads", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_community_threads_chat_room_id"))
        batch_op.drop_column("chat_room_id")

    # ### end Alembic commands ###
