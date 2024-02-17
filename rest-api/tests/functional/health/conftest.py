from __future__ import annotations

from datetime import date, timedelta
from typing import List

import pytest
from api.utils import DATE_FORMAT
from flask_sqlalchemy import SQLAlchemy
from models.patient_symptoms import PatientSymptoms
from models.symptom import Symptom
from models.users import Users

symptom_name_list = ["Nausea", "Fatigue", "Loss of Appetite"]


@pytest.fixture
def symptoms(database: SQLAlchemy) -> List[Symptom]:
    symptoms = []
    for name in symptom_name_list:
        symptom = Symptom(name=name, description="")
        database.session.add(symptom)
        symptoms.append(symptom)

    database.session.commit()
    return database.session.query(Symptom).order_by(Symptom.id).all()


@pytest.fixture
def patient_user_with_symptoms(
    database: SQLAlchemy, patient_user: Users, symptoms: List[Symptom]
) -> Users:
    base_date = date.today() - timedelta(weeks=3)
    for symptom in symptoms:
        occurrence_date = base_date
        for i in range(0, 3):
            patient_symptom = PatientSymptoms(
                occurrence_date=occurrence_date.strftime(DATE_FORMAT),
                user_profile_id=patient_user.id,
                symptom_id=symptom.id,
                note=f"Note for {symptom.name} on {occurrence_date}",
            )
            database.session.add(patient_symptom)
            occurrence_date = occurrence_date + timedelta(days=1)
        base_date = base_date + timedelta(days=1)

    database.session.commit()
    return patient_user
