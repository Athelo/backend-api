from datetime import datetime
from http.client import (
    BAD_REQUEST,
    UNPROCESSABLE_ENTITY,
)

from flask import abort, request
from flask import current_app as app
from marshmallow import Schema, ValidationError

from api.constants import DATE_FORMAT, DATETIME_FORMAT, V1_API_PREFIX


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
            except ValueError as err:
                app.logger.error(err)
                abort(UNPROCESSABLE_ENTITY, f'Unable to parse "{field_name}"')

    json_data[field_name] = full_datetime.isoformat()
    return json_data


def convertTimeStringToDateString(date_time_str: str):
    date_split = date_time_str.split("T")
    return date_split[0]


def generate_paginated_dict(api_results):
    results = []

    if isinstance(api_results, list):
        results = api_results
    elif api_results is not None:
        results.append(api_results)

    return {"count": len(results), "next": None, "previous": None, "results": results}


def get_api_url():
    return app.config.get("BASE_URL") + V1_API_PREFIX


def log_current_datetime(log_str: str):
    now = datetime.now()
    app.logger.info(f"{now}: {log_str}")


def require_json_body():
    if not request.get_json():
        abort(BAD_REQUEST, "No input data provided.")


def validate_json(json_data: dict, schema: Schema) -> dict:
    try:
        data = schema.load(json_data)

    except ValidationError as err:
        app.logger.error(err)
        abort(UNPROCESSABLE_ENTITY, err.messages)

    return data


def validate_json_body(schema: Schema) -> dict:
    require_json_body()
    return validate_json(request.get_json(), schema)
