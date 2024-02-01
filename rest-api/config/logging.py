from __future__ import annotations

import logging
import os

from flask import Flask


def setup_logging(app: Flask):
    if os.environ.get("IS_GUNICORN", False):
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
    else:
        app.logger.setLevel(logging.DEBUG)
