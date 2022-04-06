start:
	docker-compose up --build

deploy:
	set -a
	source prod.env
	set +a
	deta deploy
	deta update -e prod.env
	deta details
