import logging
from http.client import ACCEPTED, BAD_REQUEST, CREATED, NOT_FOUND, UNPROCESSABLE_ENTITY
from sqlalchemy.sql import func

from api.utils import class_route, generate_paginated_dict
from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request, is_current_user_or_403
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from models.patient_symptoms import PatientSymptoms
from models.symptom import Symptom
from schemas.user_symptom import UserSymptomSchema, UserSymptomUpdateSchema
from marshmallow import fields

logger = logging.getLogger()

user_symptom_endpoints = Blueprint(
    "My Symptoms", __name__, url_prefix="/api/v1/health/"
)


@class_route(user_symptom_endpoints, "/user_symptoms/", "my_symptoms")
class UserSymptomsView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        symptoms = (
            db.session.query(PatientSymptoms)
            .filter_by(user_profile_id=user.id)
            .join(Symptom)
            .all()
        )

        schema = UserSymptomSchema(many=True)
        res = schema.dump(symptoms)
        return generate_paginated_dict(res)

    @jwt_authenticated
    def post(self):
        user = get_user_from_request(request)
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, BAD_REQUEST
        schema = UserSymptomUpdateSchema()

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            return err.messages, UNPROCESSABLE_ENTITY

        symptom = PatientSymptoms(
            occurrence_date=data["occurrence_date"],
            user_profile_id=user.id,
            note=data.get("note", None),
            symptom_id=data["symptom_id"],
        )

        db.session.add(symptom)
        db.session.commit()
        result = schema.dump(symptom)
        return result, CREATED


@class_route(
    user_symptom_endpoints,
    "/user_symptoms/<int:symptom_id>/",
    "user_symptom_detail",
)
class UserSymptomDetailView(MethodView):
    @jwt_authenticated
    def get(self, symptom_id):
        user = get_user_from_request(request)
        symptom = db.session.get(PatientSymptoms, symptom_id)
        if symptom.user_profile_id != user.id:
            return {
                "message": f"User symptom {symptom_id} does not belong to User {user.email}"
            }, UNPROCESSABLE_ENTITY

        schema = UserSymptomSchema()
        return schema.dump(symptom)

    @jwt_authenticated
    def put(self, symptom_id):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, BAD_REQUEST
        schema = UserSymptomUpdateSchema(partial=True)

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            return err.messages, UNPROCESSABLE_ENTITY

        symptom = db.session.get(PatientSymptoms, symptom_id)
        is_current_user_or_403(request, symptom.user_profile_id)

        if symptom is None:
            return {"message": f"User Symptom {symptom_id} does not exist."}, NOT_FOUND

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
        symptom = db.session.get(PatientSymptoms, symptom_id)
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


@class_route(user_symptom_endpoints, "/user_symptoms/summary/", "my_symptoms_summary")
class UserSymptomsSummaryView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
      
        symptoms = (
            db.session.query(func.count(PatientSymptoms.symptom_id), Symptom.id, Symptom.name, Symptom.description)
            .filter_by(user_profile_id=user.id)
            .join(Symptom)
            .group_by(PatientSymptoms.symptom_id, Symptom.id, Symptom.name, Symptom.description)
            .all()
        )

        symptom_summary = []
        for symptom_data in symptoms:
            count, symptom_id, name, description = symptom_data
            symptom_summary.append({
                "occurrences_count": count,
                "symptom": {
                    "id": symptom_id,
                    "name": name,
                    "description": description
                }
            })

        return symptom_summary

@class_route(user_symptom_endpoints, "/user_feelings_and_symptoms_per_day/", "feelings_and_symptoms_per_day")
class FeelingsSymptomsPerDay(MethodView):
    @jwt_authenticated
    def get(self):
        by_symptoms = request.args.get('by_symptoms') is not None
        by_feelings = request.args.get('by_feelings') is not None

        if by_feelings:
            return {"message": "Feelings by day is not supported"}, BAD_REQUEST

        if not by_symptoms:
            return generate_paginated_dict({})

        user = get_user_from_request(request)
        symptoms = (
            db.session.query(PatientSymptoms)
            .filter_by(user_profile_id=user.id)
            .join(Symptom)
            .all()
        )

        map_by_date = {}
        date_format = '%Y-%m-%d'

        for user_sym in symptoms:
            symptom_date = user_sym.occurrence_date.strftime(date_format) 
            if symptom_date not in map_by_date:
                map_by_date[symptom_date] = set()
            
            map_by_date[symptom_date].add(user_sym.symptom.name)

        return generate_paginated_dict({k: ', '.join(v) for k,v in map_by_date.items()})