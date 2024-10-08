# Athelo Backend API

A REST API to interact with symptom tracking and messaging.

## Run App Locally
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

### Tips and tricks 
In a bash shell in the api docker container (access by running `make bash-shell`), you can run `flask routes` to see 
all routes served by the API

## Developing
VSCode is the expected environment for development. If using another editor, please find out how to configure it equivalently and update this readme

### Linting 
1. Install Ruff via extensions (VS Marketplace Link: https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
2. Create `.vscode/settings.json` if it does not exist
3. Edit the contents to be 
```
{
    "[python]": {
      "editor.codeActionsOnSave": {
        "source.fixAll": true,
        "source.organizeImports.ruff": "explicit"
      },
      "editor.defaultFormatter": "charliermarsh.ruff"
    }
}
```

### Unit tests
Before running tests for the first time, run `make create-test-db` in order to create the test db. TODO: automate this


Run all tests with `make test`. ~~To run a subset of tests, provide `TESTPATH` with the relative path
starting after `rest-api`. Example: `make test TESTPATH=api` would run all test files beneath `/rest-api/api`.~~ TODO: get test paths working again. 

If you would like to run a specific test, use `make bash-shell` to get a bash shell in the docker container and interact with pytest from there.

### Migrations
1. Make your changes to files in `rest-api/models`. Any new models must extend Base from models.base
2. Import any new models in `rest-api/models/__init__.py`
3. Run `make bash-shell`
4. In the shell, run `flask db migrate -m "<migration description>"`
5. Still in the shell, test upgrade (`flask db upgrade`) and downgrade (`flask db downgrade`)

