# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import datetime
import logging
import os

from flask import Flask, render_template, request, Response

import sqlalchemy

from connect_connector import connect_with_connector
from connect_connector_auto_iam_authn import connect_with_connector_auto_iam_authn
from connect_tcp import connect_tcp_socket
from connect_unix import connect_unix_socket

app = Flask(__name__)

logger = logging.getLogger()


def init_connection_pool() -> sqlalchemy.engine.base.Engine:
    logger.info("init connection pool")
    """Sets up connection pool for the app."""
    # use a TCP socket when INSTANCE_HOST (e.g. 127.0.0.1) is defined
    if os.environ.get("INSTANCE_HOST"):
        return connect_tcp_socket()
    logger.info("\tgot host")
    # use a Unix socket when INSTANCE_UNIX_SOCKET (e.g. /cloudsql/project:region:instance) is defined
    if os.environ.get("INSTANCE_UNIX_SOCKET"):
        return connect_unix_socket()
    logger.info("\tgot unix socket")
    # use the connector when INSTANCE_CONNECTION_NAME (e.g. project:region:instance) is defined
    if os.environ.get("INSTANCE_CONNECTION_NAME"):
        # Either a DB_USER or a DB_IAM_USER should be defined. If both are
        # defined, DB_IAM_USER takes precedence.
        logger.info("\tinstance connection provided")
        return (
            connect_with_connector_auto_iam_authn()
            if os.environ.get("DB_IAM_USER")
            else connect_with_connector()
        )

    logger.info("\t missing database connection type")
    raise ValueError(
        "Missing database connection type. Please define one of INSTANCE_HOST, INSTANCE_UNIX_SOCKET, or INSTANCE_CONNECTION_NAME"
    )


# create 'votes' table in database if it does not already exist
def migrate_db(db: sqlalchemy.engine.base.Engine) -> None:
    logger.info("migrate_db")
    """Creates the `votes` table if it doesn't exist."""
    with db.connect() as conn:
        logger.info("\tgot connection")
        conn.execute(
            sqlalchemy.text(
                "CREATE TABLE IF NOT EXISTS votes "
                "( vote_id SERIAL NOT NULL, time_cast timestamp NOT NULL, "
                "candidate VARCHAR(6) NOT NULL, PRIMARY KEY (vote_id) );"
            )
        )
        logger.info("\tconnection executed")
        conn.commit()
        logger.info("\tcommitted")


# This global variable is declared with a value of `None`, instead of calling
# `init_db()` immediately, to simplify testing. In general, it
# is safe to initialize your database connection pool when your script starts
# -- there is no need to wait for the first request.
db = None


# init_db lazily instantiates a database connection pool. Users of Cloud Run or
# App Engine may wish to skip this lazy instantiation and connect as soon
# as the function is loaded. This is primarily to help testing.
# @app.before_first_request
def init_db() -> sqlalchemy.engine.base.Engine:
    """Initiates connection to database and its structure."""
    global db
    db = init_connection_pool()
    migrate_db(db)


@app.route("/votes", methods=["GET"])
def render_index() -> str:
    """Serves the index page of the app."""
    if db is None:
        init_db()
    context = get_index_context(db)
    return render_template("index.html", **context)


@app.route("/votes", methods=["POST"])
def cast_vote() -> Response:
    """Processes a single vote from user."""
    if db is None:
        init_db()
    team = request.form["team"]
    return save_vote(db, team)


@app.route("/", methods=["GET"])
def hello_world():
    return "Hello World! This is Athelo Health's API"


# get_index_context gets data required for rendering HTML application
def get_index_context(db: sqlalchemy.engine.base.Engine) -> dict:
    """Retrieves data from the database about the votes.

    Args:
        db: Connection to the database.
    Returns:
        A dictionary containing information about votes.
    """
    votes = []
    logger.info("get index context")
    with db.connect() as conn:
        # Execute the query and fetch all results
        logger.info("\tgot db connection")
        recent_votes = conn.execute(
            sqlalchemy.text(
                "SELECT candidate, time_cast FROM votes ORDER BY time_cast DESC LIMIT 5"
            )
        ).fetchall()
        logger.info("\tgot votes")
        # Convert the results into a list of dicts representing votes
        for row in recent_votes:
            votes.append({"candidate": row[0], "time_cast": row[1]})

        stmt = sqlalchemy.text(
            "SELECT COUNT(vote_id) FROM votes WHERE candidate=:candidate"
        )
        logger.info("\t built sql text")
        # Count number of votes for tabs
        tab_count = conn.execute(stmt, parameters={"candidate": "TABS"}).scalar()
        logger.info("\tgot tab count")
        # Count number of votes for spaces
        space_count = conn.execute(stmt, parameters={"candidate": "SPACES"}).scalar()
        logger.info("\tgot space count")

    return {
        "space_count": space_count,
        "recent_votes": votes,
        "tab_count": tab_count,
    }


# save_vote saves a vote to the database that was retrieved from form data
def save_vote(db: sqlalchemy.engine.base.Engine, team: str) -> Response:
    """Saves a single vote into the database.

    Args:
        db: Connection to the database.
        team: The identifier of a team the vote is cast on.
    Returns:
        A HTTP response that can be sent to the client.
    """
    time_cast = datetime.datetime.now(tz=datetime.timezone.utc)
    # Verify that the team is one of the allowed options
    if team != "TABS" and team != "SPACES":
        logger.warning(f"Received invalid 'team' property: '{team}'")
        return Response(
            response="Invalid team specified. Should be one of 'TABS' or 'SPACES'",
            status=400,
        )

    # [START cloud_sql_postgres_sqlalchemy_connection]
    # Preparing a statement before hand can help protect against injections.
    stmt = sqlalchemy.text(
        "INSERT INTO votes (time_cast, candidate) VALUES (:time_cast, :candidate)"
    )
    try:
        # Using a with statement ensures that the connection is always released
        # back into the pool at the end of statement (even if an error occurs)
        with db.connect() as conn:
            conn.execute(stmt, parameters={"time_cast": time_cast, "candidate": team})
            conn.commit()
    except Exception as e:
        # If something goes wrong, handle the error in this section. This might
        # involve retrying or adjusting parameters depending on the situation.
        # [START_EXCLUDE]
        logger.exception(e)
        return Response(
            status=500,
            response="Unable to successfully cast vote! Please check the "
            "application logs for more details.",
        )
        # [END_EXCLUDE]
    # [END cloud_sql_postgres_sqlalchemy_connection]

    return Response(
        status=200,
        response=f"Vote successfully cast for '{team}' at time {time_cast}!",
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
