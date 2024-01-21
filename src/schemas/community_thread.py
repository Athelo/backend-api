from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.community_thread import CommunityThread
from schemas.user_profile import UserProfileSchema


class CommunityThreadSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CommunityThread
        include_relationships = True

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)


def group_message_schema_from_community_thread(
    thread: CommunityThread, belong_to: bool
):
    return {
        "id": thread.id,
        "name": thread.display_name,
        "owner": UserProfileSchema().dump(thread.owner.user),
        "chat_room_identifier": thread.id,
        "user_profiles": UserProfileSchema(many=True).dump(thread.participants),
        "chat_room_type": 2,
        "is_public": True,
        "user_profiles_count": len(thread.participants),
        "belong_to": belong_to,
    }


class CommunityThreadCreateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CommunityThread
        include_relationships = True

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    id = auto_field(dump_only=True)
