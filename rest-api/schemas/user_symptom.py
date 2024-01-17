from marshmallow import Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.patient_symptoms import PatientSymptoms
from schemas.symptom import SymptomSchema
from marshmallow import fields


class UserSymptomSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PatientSymptoms
        load_instance = True

    symptom = fields.Pluck(SymptomSchema, "name")
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)


class UserSymptomUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PatientSymptoms
        include_fk = True
        exclude = ("id", "created_at", "updated_at", "user_profile_id")
