from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.message_channel import MessageChannel


class MessageChannelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MessageChannel
        include_fk = True
