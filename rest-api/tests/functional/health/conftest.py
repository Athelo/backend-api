from __future__ import annotations

import pytest
from models.symptom import Symptom
from models.users import Users

symptom_name_list = ["Nausea", "Fatigue", "Loss of Appetite"]


@pytest.fixture
def symptoms(database):
    symptoms = []
    for name in symptom_name_list:
        symptom = Symptom(name=name, description="")
        database.session.add(symptom)
        symptoms.append(symptom)

    database.session.commit()
    return database.session.query(Symptom).all()
