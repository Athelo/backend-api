from http.client import CREATED

from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request, require_admin_user
from flask import Blueprint, request
from flask.views import MethodView
from models.database import db
from models.symptom import Symptom
from repositories.utils import commit_entity
from schemas.symptom import SymptomSchema

from api.utils import class_route, generate_paginated_dict, validate_json_body

symptom_endpoints = Blueprint("Symptom", __name__, url_prefix="/api/v1/health/symptoms")


@class_route(symptom_endpoints, "/", "symptoms")
class SyptomsView(MethodView):
    @jwt_authenticated
    def get(self):
        symptoms = db.session.scalars(db.select(Symptom)).all()
        schema = SymptomSchema(many=True)
        return generate_paginated_dict(schema.dump(symptoms))

    @jwt_authenticated
    def post(self):
        user = get_user_from_request(request)
        require_admin_user(user)
        schema = SymptomSchema()
        data = validate_json_body(schema)

        symptom = Symptom(name=data["name"], description=data["description"])
        commit_entity(symptom)
        result = schema.dump(symptom)
        return result, CREATED
