all: start test

start:
	@docker compose  up --build -d
test:
	@docker compose run --rm api pytest  -v
down:
	@docker compose  down
start_dev:
	@docker compose  up --build