from http.client import BAD_REQUEST, CREATED, OK, UNPROCESSABLE_ENTITY

from api.utils import class_route, commit_entity_or_abort, generate_paginated_dict
from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request
from flask import Blueprint, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from models.saved_content import SavedContent
from schemas.saved_content import SavedContentCreateUpdateSchema, SavedContentSchema


saved_content_endpoints = Blueprint(
    "My Saved Content", __name__, url_prefix="/api/v1/saved-content"
)


@class_route(saved_content_endpoints, "/", "saved_content")
class SavedContentView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        content = (
            db.session.query(SavedContent).filter_by(user_profile_id=user.id).all()
        )
        schema = SavedContentSchema(many=True)
        return generate_paginated_dict(schema.dump(content))

    @jwt_authenticated
    def post(self):
        user = get_user_from_request(request)
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, BAD_REQUEST
        schema = SavedContentCreateUpdateSchema()

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            return err.messages, UNPROCESSABLE_ENTITY

        saved_content = SavedContent(
            external_content_id=data["external_content_id"], user_profile_id=user.id
        )
        commit_entity_or_abort(saved_content)
        result = schema.dump(saved_content)
        return result, CREATED

    @jwt_authenticated
    def delete(self):
        user = get_user_from_request(request)
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, BAD_REQUEST
        schema = SavedContentSchema(partial=True)

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            return err.messages, UNPROCESSABLE_ENTITY

        saved_content = (
            db.session.query(SavedContent)
            .filter_by(
                user_profile_id=user.id, external_content_id=data["external_content_id"]
            )
            .one()
        )

        db.session.delete(saved_content)
        db.session.commit()
        result = schema.dump(saved_content)
        return result, OK
