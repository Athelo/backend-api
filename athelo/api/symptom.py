import logging
from http.client import BAD_REQUEST, CREATED, UNPROCESSABLE_ENTITY

from api.utils import class_route
from auth.middleware import jwt_authenticated
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from models.symptom import Symptom
from schemas.symptom import SymptomSchema

logger = logging.getLogger()

symptom_endpoints = Blueprint("Symptom", __name__, url_prefix="/api/symptoms")


@class_route(symptom_endpoints, "/", "symptoms")
class SyptomsView(MethodView):
    # TODO: admin perms?
    @jwt_authenticated
    def get(self):
        symptoms = db.session.scalars(db.select(Symptom)).all()
        schema = SymptomSchema(many=True)
        return schema.dump(symptoms)

    @jwt_authenticated
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, BAD_REQUEST
        schema = SymptomSchema()

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            return err.messages, UNPROCESSABLE_ENTITY

        symptom = Symptom(name=data["name"], description=data["description"])
        db.session.add(symptom)
        db.session.commit()
        result = schema.dump(symptom)
        return result, CREATED
