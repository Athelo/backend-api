from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.appointment import Appointment
from marshmallow import Schema, fields


class AppointmentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Appointment
        include_fk = True

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)
    status = fields.Method("get_appointment_status")

    def get_appointment_status(self, obj):
        return obj.status.value


class AppointmentCreateSchema(Schema):
    provider_id = fields.Int()
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    zoom_url = fields.Str()
    zoom_token = fields.Str()
    timezone = fields.Str(load_default="US/Mountain")
