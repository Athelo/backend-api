from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import Schema, fields
from models.community_thread import CommunityThread


class CommunityThreadSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CommunityThread
        include_relationships = True

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)


class CommunityThreadSummarySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CommunityThread
        include_relationships = False

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)
    participant_count = fields.Method("get_participant_count")

    def get_days_since_created(self, obj: CommunityThread):
        return obj.participants.count()


class CommunityThreadSummaryListSchema(Schema):
    joined_community_threads = fields.Nested(CommunityThread, many=True)
    other_community_threads = fields.Nested(CommunityThread, many=True)
