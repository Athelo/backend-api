"""update profiles for appointments

Revision ID: 9046814b7095
Revises: 1a5e56a3bbeb
Create Date: 2024-01-25 16:28:37.209540

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "9046814b7095"
down_revision = "1a5e56a3bbeb"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("appointments", schema=None) as batch_op:
        batch_op.drop_constraint("fk_appointments_patient_id_users", type_="foreignkey")
        batch_op.drop_constraint(
            "fk_appointments_provider_id_users", type_="foreignkey"
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_appointments_provider_id_provider_profiles"),
            "provider_profiles",
            ["provider_id"],
            ["id"],
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_appointments_patient_id_patient_profiles"),
            "patient_profiles",
            ["patient_id"],
            ["id"],
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table("appointments", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_appointments_patient_id_patient_profiles"),
            type_="foreignkey",
        )
        batch_op.drop_constraint(
            batch_op.f("fk_appointments_provider_id_provider_profiles"),
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            "fk_appointments_provider_id_users", "users", ["provider_id"], ["id"]
        )
        batch_op.create_foreign_key(
            "fk_appointments_patient_id_users", "users", ["patient_id"], ["id"]
        )

    # ### end Alembic commands ###
