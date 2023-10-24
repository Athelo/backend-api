from models.user_symptom import UserSymptom
from marshmallow_sqlalchemy import auto_field, SQLAlchemyAutoSchema


class UserSymptomSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserSymptom

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)
