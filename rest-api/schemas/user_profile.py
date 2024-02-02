from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.users import Users
from marshmallow import Schema, fields, post_load
from schemas.admin_profile import AdminProfileSchema
from schemas.patient_profile import PatientProfileSchema
from schemas.provider_profile import ProviderProfileSchema


class UserProfileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Users

    id = auto_field(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    display_name = fields.Str(allow_none=True)
    email = fields.Email(required=True)
    active = fields.Bool(missing=True)
    birthday = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)

    patient_profile = fields.Method("get_patient_profile")
    provider_profile = fields.Method("get_provider_profile")
    admin_profile = fields.Method("get_admin_profile")

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)

    def get_patient_profile(self, obj):
        if obj.is_patient:
            return PatientProfileSchema(
                only=[
                    "id",
                ]
            ).dump(obj.patient_profile)
        return None

    def get_provider_profile(self, obj):
        if obj.is_provider:
            return ProviderProfileSchema(
                only=[
                    "id",
                ]
            ).dump(obj.provider_profile)
        return None

    def get_admin_profile(self, obj):
        if obj.is_admin:
            return AdminProfileSchema(
                only=[
                    "id",
                ]
            ).dump(obj.admin_profile)
        return None


class UserProfileCreateSchema(Schema):
    first_name = fields.Str()
    last_name = fields.Str()
    display_name = fields.Str(allow_none=True)

    @post_load
    def slugify_name(self, in_data, **kwargs):
        if in_data.get("display_name") is None:
            in_data["display_name"] = f"{in_data['first_name']} {in_data['last_name']}"
        return in_data
