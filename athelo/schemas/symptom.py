from marshmallow_sqlalchemy import auto_field, SQLAlchemyAutoSchema
from models.symptom import Symptom


class SymptomSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Symptom

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)
