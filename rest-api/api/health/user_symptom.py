from http.client import ACCEPTED, CREATED, NOT_FOUND, UNPROCESSABLE_ENTITY

from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request, is_current_user_or_403
from flask import Blueprint, request
from flask.views import MethodView
from models.database import db
from models.patient_symptoms import PatientSymptoms
from models.symptom import Symptom
from repositories.utils import commit_entity
from schemas.patient_symptom import PatientSymptomSchema, PatientSymptomUpdateSchema
from sqlalchemy.sql import func

from api.constants import V1_API_PREFIX
from api.utils import (
    class_route,
    convertDateToDatetimeIfNecessary,
    convertTimeStringToDateString,
    generate_paginated_dict,
    require_json_body,
    validate_json,
    validate_json_body,
)

# TODO: Make all url paths kebab case
user_symptom_endpoints = Blueprint(
    "My Symptoms", __name__, url_prefix=f"{V1_API_PREFIX}/health/user_symptoms"
)


@class_route(user_symptom_endpoints, "/", "my_symptoms")
class UserSymptomListView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        symptoms = (
            db.session.query(PatientSymptoms)
            .filter_by(user_profile_id=user.id)
            .order_by(PatientSymptoms.id)
            .join(Symptom)
            .all()
        )

        schema = PatientSymptomSchema(many=True)
        res = schema.dump(symptoms)
        for result in res:
            result["occurrence_date"] = convertTimeStringToDateString(
                result["occurrence_date"]
            )

        return generate_paginated_dict(res)

    @jwt_authenticated
    def post(self):
        user = get_user_from_request(request)
        require_json_body()
        schema = PatientSymptomUpdateSchema()
        json_data = convertDateToDatetimeIfNecessary(
            request.get_json(), "occurrence_date"
        )
        data = validate_json(json_data, schema)

        symptom = PatientSymptoms(
            occurrence_date=data["occurrence_date"],
            user_profile_id=user.id,
            note=data.get("note", None),
            symptom_id=data["symptom_id"],
        )

        commit_entity(symptom)
        result = schema.dump(symptom)
        result["occurrence_date"] = convertTimeStringToDateString(
            result["occurrence_date"]
        )
        return result, CREATED


@class_route(
    user_symptom_endpoints,
    "/<int:symptom_id>/",
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

        schema = PatientSymptomSchema()
        return schema.dump(symptom)

    @jwt_authenticated
    def put(self, symptom_id):
        schema = PatientSymptomUpdateSchema(partial=True)
        data = validate_json_body(schema)

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

        commit_entity(symptom)
        result = schema.dump(symptom)
        return result, ACCEPTED

    @jwt_authenticated
    def delete(self, symptom_id):
        symptom = db.session.get(PatientSymptoms, symptom_id)
        if symptom is None:
            return {"message": f"Cannot access user symptom {symptom_id}"}, NOT_FOUND
        is_current_user_or_403(request, symptom.user_profile_id)

        schema = PatientSymptomSchema()
        json_res = schema.dump(symptom)

        db.session.delete(symptom)
        db.session.commit()

        return json_res, ACCEPTED


@class_route(user_symptom_endpoints, "/user_symptoms/summary/", "my_symptoms_summary")
class UserSymptomsSummaryView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)

        symptoms = (
            db.session.query(
                func.count(PatientSymptoms.symptom_id),
                Symptom.id,
                Symptom.name,
                Symptom.description,
            )
            .filter_by(user_profile_id=user.id)
            .join(Symptom)
            .group_by(
                PatientSymptoms.symptom_id,
                Symptom.id,
                Symptom.name,
                Symptom.description,
            )
            .all()
        )

        symptom_summary = []
        for symptom_data in symptoms:
            count, symptom_id, name, description = symptom_data
            symptom_summary.append(
                {
                    "occurrences_count": count,
                    "symptom": {
                        "id": symptom_id,
                        "name": name,
                        "description": description,
                    },
                }
            )

        return symptom_summary
