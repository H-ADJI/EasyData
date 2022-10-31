all: start test

start:
	@docker compose  up --build -d
test:
	@docker compose run --rm api pipenv run pytest  -vs
down:
	@docker compose  down
