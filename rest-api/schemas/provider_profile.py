from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.provider_profile import ProviderProfile
from marshmallow import Schema, ValidationError, fields, post_load


class ProviderProfileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ProviderProfile

    id = auto_field(dump_only=True)
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)


class ProviderProfileCreateSchema(Schema):
    appointment_buffer_sec = fields.Int()
