from http.client import BAD_REQUEST, CREATED, UNPROCESSABLE_ENTITY, NOT_FOUND, OK
import logging
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.user_profile import UserProfile
from auth.utils import get_user_from_request
from schemas.saved_content import SavedContentSchema, SavedContentCreateUpdateSchema
from models.database import db
from models.saved_content import SavedContent
from api.utils import class_route
from auth.middleware import jwt_authenticated
from auth.utils import is_current_user_or_403

logger = logging.getLogger()

saved_content_endpoints = Blueprint(
    "My Saved Content", __name__, url_prefix="/api/saved-content"
)


@class_route(saved_content_endpoints, "/", "saved_content")
class UserSymptomsView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        content = db.session.scalars(
            db.select(SavedContent).filter_by(user_profile_id=user.id)
        ).all()
        schema = SavedContentSchema(many=True)
        return schema.dump(content)

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

        db.session.add(saved_content)
        db.session.commit()
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

        saved_content = db.session.scalars(
            db.select(SavedContent).filter_by(
                user_profile_id=user.id, external_content_id=data["external_content_id"]
            )
        ).one()

        db.session.delete(saved_content)
        db.session.commit()
        result = schema.dump(saved_content)
        return result, OK
