import copy
from http.client import BAD_REQUEST

from api.utils import (
    class_route,
    generate_paginated_dict,
    convertTimeStringToDateString,
)

from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request
from api.constants import V1_API_PREFIX, DATE_FORMAT
from flask import Blueprint, request
from flask.views import MethodView
from models.database import db

from models.patient_feelings import PatientFeelings
from schemas.patient_feeling import PatientFeelingSchema

from models.symptom import Symptom
from models.patient_symptoms import PatientSymptoms
from schemas.patient_symptom import PatientSymptomSchema

RESULTS_TEMPLATE = {
    "feelings": [],
    "occurrence_date": '',
    "symptoms": [],
}

user_feeling_and_symptom_endpoints = Blueprint(
    "My Symptoms and Feelings", __name__, url_prefix=f"{V1_API_PREFIX}/health/"
)


@class_route(
    user_feeling_and_symptom_endpoints,
    "/user_feelings_and_symptoms_per_day/",
    "feelings_and_symptoms_per_day",
)
class FeelingsSymptomsPerDay(MethodView):
    @jwt_authenticated
    def get(self):
        by_symptoms = request.args.get("by_symptoms") is not None
        by_feelings = request.args.get("by_feelings") is not None

        if by_feelings:
            return {"message": "Feelings by day is not supported"}, BAD_REQUEST

        if not by_symptoms:
            return generate_paginated_dict(None)

        user = get_user_from_request(request)

        # Get feelings and responding schema
        feelings = (
            db.session.query(PatientFeelings).filter_by(user_profile_id=user.id).all()
        )
        feelings_schema = PatientFeelingSchema()

        # Get symptoms and responding schema
        symptoms = (
            db.session.query(PatientSymptoms)
            .filter_by(user_profile_id=user.id)
            .join(Symptom)
            .all()
        )
        symptoms_schema = PatientSymptomSchema()

        map_by_date = {}

        add_datapoint_to_map(map_by_date, feelings, feelings_schema, 'feelings')
        add_datapoint_to_map(map_by_date, symptoms, symptoms_schema, 'symptoms')

        return generate_paginated_dict(list(map_by_date.values()))

def add_datapoint_to_map(map, data_points, schema, data_point_name):
    for data_point in data_points:
        occurrence_date = data_point.occurrence_date.strftime(DATE_FORMAT)
        if occurrence_date not in map:
            map[occurrence_date] = copy.deepcopy(RESULTS_TEMPLATE)
            map[occurrence_date]['occurrence_date'] = occurrence_date
        
        res = schema.dump(data_point)
        res['occurrence_date'] = convertTimeStringToDateString(res['occurrence_date'])
        map[occurrence_date][data_point_name].append(res)
