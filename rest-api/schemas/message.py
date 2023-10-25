from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.message import Message


class MessageSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Message
        include_fk = True
