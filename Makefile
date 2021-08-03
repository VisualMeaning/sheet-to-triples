.PHONY: test lint check

DIR = sheet_to_triples/

check: lint test

test:
	poetry run python -m unittest discover .

lint:
	poetry run python -m flake8 $(DIR)

LIB := $(shell find $(DIR) -name "*.py")

.coverage: $(LIB)
	poetry run coverage run --source . -m unittest discover .

coverage: .coverage
	poetry run coverage report -m
