from auth.middleware import jwt_authenticated, login_required
from flask import (
    Blueprint,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask import current_app as app
from services.zoom import make_zoom_authorization_url

webapp_endpoints = Blueprint("Webapp", __name__)


@webapp_endpoints.before_request
def before_request():
    print(session)
    if "user" in session.keys():
        g.user = session.get("user")
    else:
        g.user = None


@webapp_endpoints.errorhandler(401)
def page_not_found(e):
    print("redirecting")
    return redirect(url_for("Webapp.render_login"))


@webapp_endpoints.errorhandler(Exception)
def misc_error(e):
    app.logger.error(e)
    raise e


@webapp_endpoints.route("/dev/", methods=["GET"])
@login_required
def render_dev() -> str:
    """Serves the dev tools page of the app."""
    return render_template("dev.html")


@webapp_endpoints.route("/", methods=["GET"])
@login_required
def render_index():
    print("index function")
    return render_template("index.html")


@webapp_endpoints.route(
    "/zoom/",
)
@login_required
def zoom_homepage():
    text = '<a href="%s">Authenticate with Zoom</a>'
    return text % make_zoom_authorization_url()


@webapp_endpoints.route("/video/")
@login_required
def opentok():
    key = app.config.get("VONAGE_API_KEY")
    return render_template("appointments.html", api_key=key)


@webapp_endpoints.route("/images/")
@login_required
def images():
    return render_template("image_upload.html")


@webapp_endpoints.route("/login", methods=["GET"])
def render_login(next=None):
    if request.method == "GET":
        return render_template("auth.html", redirect_url=url_for("Webapp.render_index"))


@webapp_endpoints.route("/login", methods=["POST"])
@jwt_authenticated
def set_session_from_token():
    session["user"] = request.email
    return redirect(url_for("Webapp.render_dev"))


@webapp_endpoints.route("/logout", methods=["POST"])
def clear_session():
    print("clearing session")
    if session.get("user"):
        session.pop("user")
    return redirect(url_for("Webapp.render_login"))
