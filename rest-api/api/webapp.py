from flask import Blueprint, render_template, url_for
from flask import current_app as app
from services.zoom import make_zoom_authorization_url

webapp_endpoints = Blueprint("Webapp", __name__)


@webapp_endpoints.route("/dev/", methods=["GET"])
def render_index() -> str:
    """Serves the dev tools page of the app."""
    return render_template("dev.html")


@webapp_endpoints.route(
    "/zoom/",
)
def zoom_homepage():
    text = '<a href="%s">Authenticate with Zoom</a>'
    return text % make_zoom_authorization_url()


@webapp_endpoints.route("/video/")
def opentok():
    key = app.config.get("VONAGE_API_KEY")
    return render_template("opentok.html", api_key=key)


@webapp_endpoints.route("/images/")
def images():
    return render_template("image_upload.html")


@webapp_endpoints.route("/login", methods=["GET"])
def login():
    return render_template("auth.html", redirect_url=url_for("Webapp.render_index"))
