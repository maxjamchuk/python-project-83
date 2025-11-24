PORT ?= 5000

.PHONY: install dev lint test start build render-start

install:
	uv sync

dev:
	uv run flask --debug --app page_analyzer:app run

lint:
	uv run ruff check .

test:
	uv run pytest

start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	./build.sh

render-start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
