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


class MemberDetailSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    is_online = fields.Bool()


class MessageDetailSchema(Schema):
    id = fields.Int()
    sender = fields.Str()
    text = fields.Str()
    time = fields.Str()


class MessageChannelDetailResponseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    active = fields.Bool()
    created_at = fields.Str()
    updated_at = fields.Str()
    messages = fields.List(fields.Dict())
    members = fields.List(fields.Dict())
