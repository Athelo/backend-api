"""let thread_posts.author_id be NULL for system messages

Revision ID: d28ce4eb5700
Revises: 9046814b7095
Create Date: 2024-01-27 20:23:50.579361

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d28ce4eb5700"
down_revision = "9046814b7095"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("community_threads", schema=None) as batch_op:
        batch_op.drop_index("ix_community_threads_chat_room_id")
        batch_op.drop_column("chat_room_id")

    with op.batch_alter_table("provider_availability", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_provider_availability_provider_id_users", type_="foreignkey"
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_provider_availability_provider_id_provider_profiles"),
            "provider_profiles",
            ["provider_id"],
            ["id"],
        )

    with op.batch_alter_table("thread_posts", schema=None) as batch_op:
        batch_op.alter_column("author_id", existing_type=sa.INTEGER(), nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("thread_posts", schema=None) as batch_op:
        batch_op.alter_column("author_id", existing_type=sa.INTEGER(), nullable=False)

    with op.batch_alter_table("provider_availability", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_provider_availability_provider_id_provider_profiles"),
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            "fk_provider_availability_provider_id_users",
            "users",
            ["provider_id"],
            ["id"],
        )

    with op.batch_alter_table("community_threads", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "chat_room_id",
                sa.UUID(),
                server_default=sa.text("gen_random_uuid()"),
                autoincrement=False,
                nullable=False,
            )
        )
        batch_op.create_index(
            "ix_community_threads_chat_room_id", ["chat_room_id"], unique=True
        )

    # ### end Alembic commands ###
