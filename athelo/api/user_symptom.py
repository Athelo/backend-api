from http.client import BAD_REQUEST, CREATED, UNPROCESSABLE_ENTITY, NOT_FOUND, ACCEPTED
import logging
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from schemas.user_symptom import UserSymptomSchema, UserSymptomUpdateSchema
from models import db
from models.user_symptom import UserSymptom
from api.utils import class_route

logger = logging.getLogger()
# Create a user blueprint
user_symptom_endpoints = Blueprint("User Symptoms", __name__, url_prefix="/api/users")


@class_route(user_symptom_endpoints, "/<int:user_profile_id>/symptoms", "user_symptoms")
class UserSymptomsView(MethodView):
    def get(self, user_profile_id: int):
        users = db.session.scalars(
            db.select(UserSymptom).filter_by(user_profile_id=user_profile_id)
        ).all()
        schema = UserSymptomSchema(many=True)
        return schema.dump(users)

    def post(self, user_profile_id):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, BAD_REQUEST
        schema = UserSymptomUpdateSchema()

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            return err.messages, UNPROCESSABLE_ENTITY

        symptom = UserSymptom(
            occurrence_date=data["occurrence_date"],
            user_profile_id=user_profile_id,
            note=data.get("note", None),
            symptom_id=data["symptom_id"],
        )

        db.session.add(symptom)
        db.session.commit()
        result = schema.dump(symptom)
        return result, CREATED


@class_route(
    user_symptom_endpoints,
    "/<int:user_profile_id>/symptom/<int:symptom_id>",
    "user_symptom_detail",
)
class UserSymptomDetailView(MethodView):
    def get(self, user_profile_id, symptom_id):
        symptom = db.session.get(UserSymptom, symptom_id)
        if symptom.user_profile_id != user_profile_id:
            return {
                "message": f"User symptom {symptom_id} does not belong to User {user_profile_id}"
            }, UNPROCESSABLE_ENTITY

        schema = UserSymptomSchema()
        return schema.dump(symptom)

    def put(self, user_profile_id, symptom_id):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, BAD_REQUEST
        schema = UserSymptomUpdateSchema(partial=True)

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            return err.messages, UNPROCESSABLE_ENTITY

        symptom = db.session.get(UserSymptom, symptom_id)
        if symptom is None:
            return {
                "message": f"User Symptom {user_profile_id} does not exist."
            }, NOT_FOUND

        if data.get("user_profile_id"):
            return {
                "message": "Cannot change user profile id of a submitted user symptom"
            }, UNPROCESSABLE_ENTITY

        if data.get("occurrence_date"):
            symptom.occurrence_date = data["occurrence_date"]
        if data.get("note"):
            symptom.note = data["note"]
        if data.get("symptom_id"):
            symptom.symptom_id = data["symptom_id"]

        db.session.add(symptom)
        db.session.commit()
        result = schema.dump(symptom)
        return result, ACCEPTED

    def delete(self, user_profile_id, symptom_id):
        schema = UserSymptomSchema()
        symptom = db.session.get(UserSymptom, symptom_id)
        if symptom is None:
            return {
                "message": f"User Symptom {user_profile_id} does not exist."
            }, NOT_FOUND

        if symptom.user_profile_id != user_profile_id:
            return {
                "message": f"User symptom {symptom_id} does not belong to User {user_profile_id}"
            }, UNPROCESSABLE_ENTITY

        db.session.delete(symptom)
        db.session.commit()
        return schema.dump(symptom), ACCEPTED
