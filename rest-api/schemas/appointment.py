from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.message import Message


class AppointmentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Message
        include_fk = True

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)
