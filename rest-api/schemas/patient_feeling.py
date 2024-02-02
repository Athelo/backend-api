from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.patient_feelings import PatientFeelings


class PatientFeelingSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PatientFeelings 
        load_instance = True

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)


class PatientFeelingUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PatientFeelings 
        exclude = ("created_at", "updated_at", "user_profile_id")
