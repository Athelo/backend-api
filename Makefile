.PHONY: 
	help

help: 
	@./help.sh $(MAKEFILE_LIST)

build-up: ## Build and run docker containers
	docker-compose up --build -d 

postgres-shell: ## Open psql shell in local db
	docker-compose exec db psql --username=athelo --dbname=athelo

flask-shell: ## Open flask shell in api container
	docker-compose exec athelo-backend-api flask shell

pdb: ## Attach to python container to debug
	docker attach "$(docker-compose ps -q athelo-backend-api)"