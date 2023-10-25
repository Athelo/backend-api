from marshmallow_sqlalchemy import auto_field, SQLAlchemyAutoSchema
from models.saved_content import SavedContent


class SavedContentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SavedContent
        include_fk = True

    created_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)


class SavedContentCreateUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SavedContent
        exclude = ("id", "created_at", "user_profile_id")
