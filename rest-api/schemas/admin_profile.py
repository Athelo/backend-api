from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.fields import Nested
from models.admin_profile import AdminProfile
from marshmallow import Schema, fields, post_load


class AdminProfileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = AdminProfile
        include_fk = True

    id = auto_field(dump_only=True)

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
