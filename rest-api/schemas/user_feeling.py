from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.user_feeling import UserFeeling


class UserFeelingSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserFeeling 
        load_instance = True

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)


class UserFeelingUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserFeeling 
        exclude = ("id", "created_at", "updated_at", "user_profile_id")
