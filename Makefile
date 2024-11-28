.PHONY: build up down bash
COMPOSE=docker-compose $(COMPOSE_OPTS)
USER_ID := $(shell id -u)
GROUP_ID := $(shell id -g)

build:
	$(COMPOSE) build --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID)

up: build
	$(COMPOSE) up

down:
	$(COMPOSE) down --rmi all --volumes --remove-orphans

bash:
	$(COMPOSE) exec django bash
