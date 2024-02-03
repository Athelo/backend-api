"""new_user_profiles

Revision ID: da15cb874d6d
Revises: ebaf5e58f37a
Create Date: 2024-01-20 23:56:59.109632

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.exc import ProgrammingError

# revision identifiers, used by Alembic.
revision = 'da15cb874d6d'
down_revision = 'ebaf5e58f37a'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    profiles = sa.sql.table("profiles", sa.Column("birthday", sa.VARCHAR()))

    # can't do `is None` because of alembic/sqlalchemy
    op.execute(
       profiles.update().where(profiles.c.birthday == None).values(birthday=" ")
    )

    profiles = sa.sql.table("profiles", sa.Column("phone", sa.VARCHAR()))
    op.execute(
       profiles.update().where(profiles.c.phone == None).values(phone=" ")
    )
    # ### end Alembic commands ###
    cancer_status_enum = ENUM('ACTIVE', 'REMISSION', name='cancerstatusenum', metadata=sa.MetaData(), create_type=False)
    bind = op.get_bind()
    insp = sa.engine.reflection.Inspector.from_engine(bind)
    if 'cancerstatusenum' not in [e['name'] for e in insp.get_enums()]:
        try:
            cancer_status_enum.create(bind=bind, checkfirst=True)
        except ProgrammingError:
            pass 
        
    op.rename_table('profiles', 'users')
    op.rename_table('user_feelings','patient_feelings')
    op.rename_table('user_symptoms','patient_symptoms')
    
    op.create_table('patient_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False), 

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_patient_profiles_user_id')),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('cancer_status', cancer_status_enum, nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_patient_profiles'))
    )
    
    op.create_table('provider_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),  
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_provider_profiles_user_id')),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('appointment_buffer_sec', sa.Integer()),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_provider_profiles'))
    )
    
    op.create_table('caregiver_profiles',
        sa.Column('id', sa.Integer, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_caregiver_profiles_user_id')),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_caregiver_profiles'))
    )
    
    op.create_table('admin_profiles',
        sa.Column('id', sa.Integer, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False), 
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_admin_profiles_user_id')),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_admin_profiles'))
    )
    # ### end Alembic commands ###


def downgrade():
    op.drop_table('admin_profiles')
    op.drop_table('caregiver_profiles')
    op.drop_table('provider_profiles')
    op.drop_table('patient_profiles')
    
    op.rename_table('patient_symptoms','user_symptoms')
    op.rename_table('patient_feelings','user_feelings')
    op.rename_table('users','profiles')
    
    cancer_status_enum = ENUM('ACTIVE', 'REMISSION', name='cancerstatusenum', metadata=sa.MetaData())

    cancer_status_enum.drop(bind=op.get_bind(), checkfirst=True)
    
    profiles = sa.sql.table("profiles", 
       sa.Column("birthday", sa.VARCHAR()),
       sa.Column("phone", sa.VARCHAR())
    )

    # Set birthday and phone back to None where they are empty strings
    op.execute(
       profiles.update().where(profiles.c.birthday == "").values(birthday=None)
    )
    op.execute(
       profiles.update().where(profiles.c.phone == "").values(phone=None)
    )
    # ### end Alembic commands ###
