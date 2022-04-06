start:
	docker-compose up --build

test:
	docker-compose build
	docker-compose run api python3 -m pytest

deploy:
	deta deploy
	deta update -e prod.env
	deta details
