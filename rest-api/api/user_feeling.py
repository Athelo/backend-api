import logging
from http.client import BAD_REQUEST, CREATED, UNPROCESSABLE_ENTITY

from api.utils import (
    class_route,
    generate_paginated_dict,
    commit_entity_or_abort,
    convertDateToDatetimeIfNecessary,
)
from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request
from flask import Blueprint, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from models.patient_feelings import PatientFeelings
from schemas.patient_feeling import PatientFeelingSchema, PatientFeelingUpdateSchema


user_feeling_endpoints = Blueprint(
    "My Feelings", __name__, url_prefix="/api/v1/health/"
)


@class_route(user_feeling_endpoints, "/user_feeling/", "my_feelings")
class UserFeelingsView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        feelings = (
            db.session.query(PatientFeelings).filter_by(user_profile_id=user.id).all()
        )

        schema = PatientFeelingSchema(many=True)
        res = schema.dump(feelings)
        return generate_paginated_dict(res)

    @jwt_authenticated
    def post(self):
        user = get_user_from_request(request)
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, BAD_REQUEST

        json_data = convertDateToDatetimeIfNecessary(json_data, "occurrence_date")

        schema = PatientFeelingUpdateSchema()

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            return err.messages, UNPROCESSABLE_ENTITY

        feeling = PatientFeelings(
            occurrence_date=data["occurrence_date"],
            user_profile_id=user.id,
            note=data.get("note", None),
            general_feeling=data["general_feeling"],
        )
        commit_entity_or_abort(feeling)
        result = schema.dump(feeling)
        return result, CREATED
