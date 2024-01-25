"""add feedback entities

Revision ID: 1a5e56a3bbeb
Revises: 60b34ef1f663
Create Date: 2024-01-25 03:34:39.726008

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "1a5e56a3bbeb"
down_revision = "60b34ef1f663"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "feedback_topics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_feedback_topics")),
    )
    op.create_table(
        "feedbacks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"], ["users.id"], name=op.f("fk_feedbacks_author_id_users")
        ),
        sa.ForeignKeyConstraint(
            ["topic_id"],
            ["feedback_topics.id"],
            name=op.f("fk_feedbacks_topic_id_feedback_topics"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_feedbacks")),
    )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.drop_table("feedbacks")
    op.drop_table("feedback_topics")
    # ### end Alembic commands ###