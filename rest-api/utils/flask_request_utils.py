from typing import Union

import flask


def get_json_body(req: flask.Request) -> Union[list, dict]:
    try:
        body = req.json or {}
    except Exception:
        body = {}

    return body


def get_request_json_dict_or_raise_exception(req: flask.Request) -> dict:
    body = get_json_body(req)
    if not body or not isinstance(body, dict):
        raise Exception("Request json should be an object")

    return body
