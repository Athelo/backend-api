#!/bin/bash

set -e
set -x

# upgrade db 
flask db upgrade
EXPOSE 8080
# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
#gunicorn --bind :$PORT --workers 8 --timeout 0 app:app
gunicorn --bind  0.0.0.0:8080 --worker-class eventlet -w 1 --threads 8 app:app
