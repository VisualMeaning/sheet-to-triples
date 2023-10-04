.PHONY: test lint fix check coverage install all

DIR = sheet_to_triples/

all: install check

poetry.lock: pyproject.toml
	poetry lock && touch poetry.lock -r pyproject.toml

install: poetry.lock
	poetry install

check: lint test

test:
	poetry run python -m unittest discover .

lint:
	poetry run python -m ruff $(DIR)

fix:
	poetry run python -m ruff $(DIR) --fix

LIB := $(shell find $(DIR) -name "*.py")

.coverage: $(LIB)
	poetry run coverage run --source . -m unittest discover .

coverage: .coverage
	poetry run coverage report -m
