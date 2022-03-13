SHELL := /bin/bash
.DEFAULT_GOAL := build-images
silent=false

build-images:
	@docker build -f Dockerfile . -t ngo:local

start:
	@docker-compose up -d