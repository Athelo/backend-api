FROM python:3.11

COPY requirements.txt /

RUN pip install -r /requirements.txt

ADD . /flask_app
WORKDIR /flask_app

EXPOSE 5000

CMD gunicorn 'flask_app:create_app()' \
    --worker-class eventlet \
    -w 1 \
    --threads 8 \
    --bind 0.0.0.0:5000 \
    --reload \
    --access-logfile - \
    --error-logfile -


