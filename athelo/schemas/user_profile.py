from marshmallow_sqlalchemy import auto_field, SQLAlchemyAutoSchema
from models.user_profile import UserProfile


class UserProfileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserProfile

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)
