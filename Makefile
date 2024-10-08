.DEFAULT_GOAL := help

TESTPATH ?= ./

.PHONY: help test

help: 
	@./help.sh $(MAKEFILE_LIST)

build-up: ## Build and run docker containers
	docker-compose up --build -d 

postgres-shell: ## Open psql shell in local db
	docker-compose exec db psql --username=athelo --dbname=athelo

flask-shell: ## Open flask shell in api container
	docker-compose exec -it athelo-backend-api flask shell

bash-shell: ## Open bash shell in api container
	docker-compose exec -it athelo-backend-api bash

db-shell:
	docker-compose exec -it db psql --username=athelo --dbname=athelo

pdb: ## Attach to python container to debug (after adding import pdb; pdb.set_trace())
	docker attach "$(docker-compose ps -q athelo-backend-api)"

refresh-adc: ## refresh app default credentials so auth works
	gcloud auth application-default login
	cp ~/.config/gcloud/application_default_credentials.json .

test: ## run pytest
	docker-compose exec athelo-backend-api env ENVIRONMENT=test TERM=xterm-256color bash -c pytest ${TESTPATH} --disable-warnings

create-test-db: ## create test db for pytests
	docker-compose exec db sh -c 'psql --username=athelo --dbname=athelo -c "create database athelotest"'