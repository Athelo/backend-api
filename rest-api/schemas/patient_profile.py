from marshmallow import Schema, ValidationError, fields, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.patient_profile import CancerStatus, PatientProfile


class PatientProfileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PatientProfile

    id = auto_field(dump_only=True)
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    cancer_status = fields.Method("get_cancer_status")

    def get_cancer_status(self, obj):
        return obj.cancer_status.value


class PatientProfileCreateSchema(Schema):
    active = fields.Bool(load_default=True)  # Default to True if not provided
    cancer_status = fields.Str(required=True)

    @post_load
    def validate_cancer_status(self, data, **kwargs):
        if data.get("cancer_status") not in CancerStatus._member_names_:
            raise ValidationError(
                f"Invalid cancer status: {data.get('cancer_status')} not in {CancerStatus._member_names_}"
            )
        data["cancer_status"] = CancerStatus[data["cancer_status"]]
        return data
