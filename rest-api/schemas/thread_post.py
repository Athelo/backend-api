from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.thread_post import ThreadPost


class ThreadPostSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ThreadPost
        include_fk = True

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)


class ThreadPostCreateSchema(Schema):
    content = fields.Str()
