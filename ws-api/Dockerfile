FROM python:3.11

COPY requirements.txt /

RUN pip install -r /requirements.txt

ADD . /app
WORKDIR /app

CMD gunicorn app:app \
    --worker-class eventlet \
    -w 1 \
    --threads 8 \
    --bind 0.0.0.0:8081 \
    --reload \
    --access-logfile - \
    --error-logfile -
