from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.provider_profile import ProviderProfile, ProviderType
from marshmallow import Schema, fields


class ProviderProfileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ProviderProfile

    id = auto_field(dump_only=True)
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    provider_type = fields.Method("get_provider_type")

    def get_provider_type(self, obj):
        return obj.provider_type.value


class ProviderProfileCreateSchema(Schema):
    appointment_buffer_sec = fields.Int(required=True)
    provider_type = fields.Str()
