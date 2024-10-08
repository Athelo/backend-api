from http.client import CREATED

from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request
from flask import Blueprint, request
from flask.views import MethodView
from models.database import db
from models.patient_feelings import PatientFeelings
from repositories.utils import commit_entity
from schemas.patient_feeling import PatientFeelingSchema, PatientFeelingUpdateSchema

from api.constants import V1_API_PREFIX
from api.utils import (
    class_route,
    convertDateToDatetimeIfNecessary,
    convertTimeStringToDateString,
    generate_paginated_dict,
    require_json_body,
    validate_json,
)

user_feeling_endpoints = Blueprint(
    "My Feelings", __name__, url_prefix=f"{V1_API_PREFIX}/health/"
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
        for result in res:
            result["occurrence_date"] = convertTimeStringToDateString(
                result["occurrence_date"]
            )

        return generate_paginated_dict(res)

    @jwt_authenticated
    def post(self):
        user = get_user_from_request(request)
        require_json_body()
        json_data = convertDateToDatetimeIfNecessary(
            request.get_json(), "occurrence_date"
        )

        schema = PatientFeelingUpdateSchema()
        data = validate_json(json_data, schema)

        feeling = PatientFeelings(
            occurrence_date=data["occurrence_date"],
            user_profile_id=user.id,
            note=data.get("note", None),
            general_feeling=data["general_feeling"],
        )
        commit_entity(feeling)
        result = schema.dump(feeling)
        result["occurrence_date"] = convertTimeStringToDateString(
            result["occurrence_date"]
        )
        return result, CREATED
