build:
	@docker build -f Dockerfile . -t ngo-python-api:local

start:
	@docker run -it --env-file prod.env -p 8000:8000 ngo-python-api:local