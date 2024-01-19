from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.fields import Nested
from models.users import Users
from marshmallow import Schema, fields, post_load

class UserProfileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Users

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)
    patient_profile = Nested('PatientProfileSchema', many=False, exclude=('user',))


class UserProfileCreateSchema(Schema):
    first_name = fields.Str()
    last_name = fields.Str()
    display_name = fields.Str(allow_none=True)

    @post_load
    def slugify_name(self, in_data, **kwargs):
        if in_data.get("display_name") is None:
            in_data["display_name"] = f"{in_data['first_name']} {in_data['last_name']}"
        return in_data
