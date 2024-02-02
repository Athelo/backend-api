from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.admin_profile import AdminProfile


class AdminProfileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = AdminProfile

    id = auto_field(dump_only=True)

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
