from api.constants import V1_API_PREFIX, DATE_FORMAT, DATETIME_FORMAT
from flask import current_app as app
from flask import abort
from models.database import db
from models.base import Base
from http.client import UNPROCESSABLE_ENTITY
from datetime import datetime


# decorator code
def class_route(self, rule, endpoint, **options):
    """
    This decorator allow add routed to class view.
    :param self: any flask object that have `add_url_rule` method.
    :param rule: flask url rule.
    :param endpoint: endpoint name
    """

    def decorator(cls):
        self.add_url_rule(rule, view_func=cls.as_view(endpoint), **options)
        return cls

    return decorator


def generate_paginated_dict(api_results):
    results = []

    if isinstance(api_results, list):
        results = api_results
    elif api_results is not None:
        results.append(api_results)

    return {"count": len(results), "next": None, "previous": None, "results": results}


def get_api_url():
    return app.config.get("BASE_URL") + V1_API_PREFIX


def convertDateToDatetimeIfNecessary(json_data: dict, field_name: str):
    try:
        full_datetime = datetime.fromisoformat(
            json_data[field_name],
        )
    except ValueError:
        try:
            full_datetime = datetime.strptime(json_data[field_name], DATETIME_FORMAT)
        except ValueError:
            try:
                full_datetime = datetime.strptime(json_data[field_name], DATE_FORMAT)
            except ValueError:
                abort(UNPROCESSABLE_ENTITY, f'Unable to parse "{field_name}"')

    json_data[field_name] = full_datetime.isoformat()
    return json_data


def convertTimeStringToDateString(date_time_str: str):
    date_split = date_time_str.split("T")
    return date_split[0]
