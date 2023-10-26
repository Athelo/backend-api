from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import Schema, fields
from models.message_channel import MessageChannel


class MessageChannelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MessageChannel
        include_relationships = True

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)


class MessageChannelRequestSchema(Schema):
    users = fields.List(fields.Int)
