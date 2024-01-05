import logging
from http.client import ACCEPTED, BAD_REQUEST, CREATED, NOT_FOUND, UNPROCESSABLE_ENTITY

from api.utils import class_route
from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from schemas.user_profile import UserProfileSchema
from api.constants import USER_PROFILE_RETURN_SCHEMA

logger = logging.getLogger()

my_profile_endpoints = Blueprint("My Profile", __name__, url_prefix="/api/v1/users/me")


@class_route(my_profile_endpoints, "/", "my_profile_detail")
class UserProfileDetailView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        results = []

        if user:
            res = USER_PROFILE_RETURN_SCHEMA.copy()
            res["id"] = user.id
            res["first_name"] = user.first_name
            res["last_name"] = user.last_name
            res["display_name"] = user.display_name
            res["email"] = user.email
            results.append(res)
    
        return {
            "count":len(results),
            "next":None,
            "previous":None,
            "results": results 
        }

    @jwt_authenticated
    def put(self):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, BAD_REQUEST
        schema = UserProfileSchema(partial=True)

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            return err.messages, UNPROCESSABLE_ENTITY

        user = get_user_from_request(request)

        if user is None:
            return {
                "message": f"User Profile for {request.email} does not exist."
            }, NOT_FOUND

        if data.get("first_name"):
            user.first_name = data["first_name"]
        if data.get("last_name"):
            user.last_name = data["last_name"]
        if data.get("display_name"):
            user.display_name = data["display_name"]
        if data.get("email"):
            user.email = (data["email"],)
        if data.get("active"):
            user.active = (data.get("active", True),)

        db.session.add(user)
        db.session.commit()
        result = schema.dump(user)
        return result, ACCEPTED


@class_route(my_profile_endpoints, "/delete/", "delete-profile")
class UserProfileDeleteView(MethodView):
    @jwt_authenticated
    def delete(self):
        user = get_user_from_request(request)
        db.session.delete(user)
        db.session.commit()
        return {}, ACCEPTED