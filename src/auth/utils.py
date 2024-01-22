from flask import Request
from models.database import db
from models.users import Users
from werkzeug.exceptions import Unauthorized, NotFound
from sqlalchemy.exc import NoResultFound

import logging

logger = logging.getLogger()


def get_user_from_request(request: Request) -> Users:
    try:
        user = db.session.query(Users).filter_by(email=request.email).one()
        return user
    except NoResultFound:
        raise NotFound("User profile does not exist for that email")


def is_current_user_or_403(request, user_id):
    user = get_user_from_request(request)
    if user_id != user.id:
        raise Unauthorized()
