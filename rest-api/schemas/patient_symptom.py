from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.patient_symptoms import PatientSymptoms

from schemas.symptom import SymptomSchema


class PatientSymptomSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PatientSymptoms
        load_instance = True

    symptom = fields.Nested(SymptomSchema)
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)


class PatientSymptomUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PatientSymptoms
        include_fk = True
        exclude = ("created_at", "updated_at", "user_profile_id")
