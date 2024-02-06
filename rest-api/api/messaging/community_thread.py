from http.client import ACCEPTED, CONFLICT, CREATED, NOT_FOUND, OK

from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request, require_admin_user
from flask import Blueprint, abort, request
from flask.views import MethodView
from models.community_thread import CommunityThread, ThreadParticipants
from models.database import db
from repositories.utils import commit_entity
from schemas.community_thread import (
    CommunityThreadCreateSchema,
    CommunityThreadSchema,
    group_message_schema_from_community_thread,
)

from api.constants import V1_API_PREFIX
from api.utils import class_route, generate_paginated_dict, validate_json_body

community_thread_endpoints = Blueprint(
    # "Community Threads", __name__, url_prefix=f"{V1_API_PREFIX}/community-threads"
    "Community Threads",
    __name__,
    url_prefix=f"{V1_API_PREFIX}/chats/group-conversations",
)


@class_route(community_thread_endpoints, "/", "community_thread_list")
class CommunityThreadListView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        # TODO: optimize to pull the set of joined/unjoined from the db instead of filtering in python
        user_threads = (
            db.session.query(ThreadParticipants.thread_id)
            .where(ThreadParticipants.user_profile_id == user.id)
            .all()
        )
        user_thread_ids = [thread[0] for thread in user_threads]
        joined_community_threads = (
            db.session.query(CommunityThread)
            .where(CommunityThread.id.in_(user_thread_ids))
            .where(CommunityThread.active.is_(True))
            .all()
        )

        unjoined_community_threads = (
            db.session.query(CommunityThread)
            .where(CommunityThread.id.notin_(user_thread_ids))
            .all()
        )

        joined_group_messages = [
            group_message_schema_from_community_thread(thread, True)
            for thread in joined_community_threads
        ]
        not_joined_group_messagees = [
            group_message_schema_from_community_thread(thread, False)
            for thread in unjoined_community_threads
        ]
        results = joined_group_messages + not_joined_group_messagees
        return generate_paginated_dict(results)

    @jwt_authenticated
    def put(self):
        user = get_user_from_request(request)
        require_admin_user(user)

        schema = CommunityThreadCreateSchema()
        data = validate_json_body(schema)

        thread = CommunityThread(
            display_name=data["display_name"],
            description=data["description"],
            owner_id=user.admin_profile.id,
            participants=[user],
        )
        commit_entity(thread)
        result = CommunityThreadSchema().dump(thread)
        return result, CREATED


@community_thread_endpoints.route("/<int:thread_id>/", methods=["GET"])
@jwt_authenticated
def get_community_thread(thread_id: int):
    user = get_user_from_request(request)
    community_thread = (
        db.session.query(CommunityThread)
        .where(CommunityThread.id == thread_id)
        .join(CommunityThread.participants)
        .one_or_none()
    )

    belong_to = any(
        participant
        for participant in community_thread.participants
        if participant.id == user.id
    )

    return group_message_schema_from_community_thread(community_thread, belong_to), OK


@community_thread_endpoints.route("/<int:thread_id>/", methods=["POST"])
@jwt_authenticated
def update_community_thread(thread_id: int):
    user = get_user_from_request(request)
    require_admin_user(user)
    schema = CommunityThreadCreateSchema(partial=True)

    data = validate_json_body(schema)

    thread = db.session.get(CommunityThread, thread_id)
    if thread is None:
        abort(NOT_FOUND, f"Thread {thread_id} not found")

    # TODO: flesh out as more edit capability is needed
    if data.get("display_name"):
        thread.display_name = data["display_name"]
    if data.get("description"):
        thread.description = data["description"]
    if data.get("active"):
        thread.active = data["active"]

    commit_entity(thread)

    result = CommunityThreadSchema().dump(thread)
    return result, ACCEPTED


@community_thread_endpoints.route("/<int:thread_id>/join/", methods=["PUT"])
@jwt_authenticated
def join_community_thread(thread_id: int):
    user = get_user_from_request(request)
    community_thread = db.session.get(CommunityThread, thread_id)

    if community_thread is None:
        abort(NOT_FOUND, f"thread {thread_id} does not exist")

    if any(
        participant
        for participant in community_thread.participants
        if participant.id == user.id
    ):
        abort(CONFLICT, f"User {user.id} is already in thread {thread_id}")

    community_thread.participants.append(user)
    commit_entity(community_thread)
    return "", ACCEPTED


@community_thread_endpoints.route("/<int:thread_id>/leave/", methods=["PUT"])
@jwt_authenticated
def leave_community_thread(thread_id: int):
    user = get_user_from_request(request)
    community_thread = (
        db.session.query(CommunityThread)
        .where(CommunityThread.id == thread_id)
        .join(CommunityThread.participants)
        .one_or_none()
    )

    if community_thread is None:
        abort(NOT_FOUND, f"thread {thread_id} does not exist")

    if not any(
        participant
        for participant in community_thread.participants
        if participant.id == user.id
    ):
        abort(CONFLICT, f"User {user.id} is not in thread {community_thread.id}")

    if user.is_admin and community_thread.owner_id == user.admin_profile.id:
        abort(CONFLICT, "Thread owner cannot leave thread")

    community_thread.participants.remove(user)
    commit_entity(community_thread)

    return "", ACCEPTED
