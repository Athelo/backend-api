from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.patient_profile import CancerStatus, PatientProfile
from marshmallow import Schema, ValidationError, fields, post_load


class PatientProfileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PatientProfile

    id = auto_field(dump_only=True)
    user_id = auto_field(dump_only=True)
    active = auto_field()
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    cancer_status = auto_field()


class PatientProfileCreateSchema(Schema):
    user_id = fields.Int(required=True)
    active = fields.Bool(missing=True)  # Default to True if not provided
    cancer_status = fields.Str(required=True)

    @post_load
    def validate_cancer_status(self, data, **kwargs):
        if data.get("cancer_status") not in CancerStatus._member_names_:
            raise ValidationError("Invalid cancer status")
        data["cancer_status"] = CancerStatus[data["cancer_status"]]
        return data
