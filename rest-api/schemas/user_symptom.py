from marshmallow import Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.user_symptom import UserSymptom
from schemas.symptom import SymptomSchema
from marshmallow import fields


class UserSymptomSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserSymptom
        load_instance = True

    symptom = fields.Pluck(SymptomSchema, "name")
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)


class UserSymptomUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserSymptom
        include_fk = True
        exclude = ("id", "created_at", "updated_at", "user_profile_id")