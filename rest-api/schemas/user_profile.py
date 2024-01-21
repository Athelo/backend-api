from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.fields import Nested
from models.users import Users
from marshmallow import Schema, fields, post_load
# from schemas.

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
    
    patient_feelings = Nested("PatientFeelingsSchema", many=True, exclude=('user',), dump_only=True)
    patient_symptoms = Nested("PatientSymptomsSchema", many=True, exclude=('user',), dump_only=True)
    saved_content = Nested("SavedContentSchema", many=True, exclude=('user',), dump_only=True)
    patient_profiles = Nested("PatientProfilesSchema", many=False, exclude=('user',), dump_only=True)
    admin_profiles = Nested("AdminProfilesSchema", many=False, exclude=('user',), dump_only=True)
    caregiver_profiles = Nested("CaregiverProfilesSchema", many=False, exclude=('user',), dump_only=True)
    provider_profiles = Nested("ProviderProfilesSchema", many=False, exclude=('user',), dump_only=True)
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)


class UserProfileCreateSchema(Schema):
    first_name = fields.Str()
    last_name = fields.Str()
    display_name = fields.Str(allow_none=True)

    @post_load
    def slugify_name(self, in_data, **kwargs):
        if in_data.get("display_name") is None:
            in_data["display_name"] = f"{in_data['first_name']} {in_data['last_name']}"
        return in_data
