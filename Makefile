.PHONY: test lint check

test:
	poetry run python -m unittest discover .

lint: 
	poetry run python -m flake8

check: test lint

LIB := $(shell find sheet_to_triples/ -name "*.py")

.coverage: $(LIB)
	poetry run coverage run --source . -m unittest discover .

coverage: .coverage
	poetry run coverage report -m
