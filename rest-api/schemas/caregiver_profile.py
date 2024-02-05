from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.caregiver_profile import CaregiverProfile


class CaregiverProfileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CaregiverProfile
        include_fk = False

    id = auto_field(dump_only=True)

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
