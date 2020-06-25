FROM ubuntu:20.04

RUN apt-get update && \
	apt-get install -y python3 python3-pip python3-venv postgrseql-client git tmux libpq-dev postgresql-client && \
	pip3 install poetry

COPY . /app
WORKDIR /app
RUN python3 -m poetry install
