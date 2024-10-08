from http.client import UNAUTHORIZED

from flask import Request, abort
from models.users import Users
from repositories.user import get_user_by_email
from werkzeug.exceptions import NotFound, Unauthorized


def get_user_from_request(request: Request) -> Users:
    user = get_user_by_email(request.email)
    if user is None:
        raise NotFound("User profile does not exist for that email")

    return user


def is_current_user_or_403(request, user_id) -> None:
    user = get_user_from_request(request)
    if user_id != user.id:
        raise Unauthorized()


def require_admin_user(
    user: Users, message: str = "Only admins can perform this action"
) -> None:
    if not user.is_admin:
        abort(UNAUTHORIZED, message)


def require_provider_user(
    user: Users, message: str = "Only providers can perform this action"
) -> None:
    if not user.provider_profile:
        abort(UNAUTHORIZED, message)
