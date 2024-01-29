#!/bin/bash

set -e
set -x

# upgrade db 
flask db upgrade

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
gunicorn --bind :$PORT --worker-class eventlet --workers 8 --timeout 0 app:app
