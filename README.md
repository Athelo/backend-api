# Athelo Backend and Websocket API

A REST API to interact with symptom tracking and messaging.

## Run App Locally

### With Docker Compose
After installing Docker and docker-compose, run
```
make build-run
```
to bring up a debug mode API container and a local postgres db container.

If you want imports to be recognized by your IDE, create a virtual environment
and install the dependecies locally. 
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
#### Migrations
1. Make your changes to files in `rest-api/models`. Any new models must extend Base from models.base
2. Import any new models in `rest-api/models/__init__.py`
3. Run `make bash-shell`
4. In the shell, run `flask db migrate -m "<migration description>"`
5. Still in the shell, test upgrade (`flask db upgrade`) and downgrade (`flask db downgrade`)

#### Tips and tricks 
In a bash shell in the api docker container (access by running `make bash-shell`), you can run `flask routes` to see 
all routes served by the API
