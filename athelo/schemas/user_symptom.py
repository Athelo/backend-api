from marshmallow import Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.user_symptom import UserSymptom


class UserSymptomSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserSymptom
        include_fk = True

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)


class UserSymptomUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserSymptom
        include_fk = True
        exclude = ("id", "created_at", "updated_at", "user_profile_id")
