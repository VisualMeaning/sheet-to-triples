.PHONY: test lint check

test:
	poetry run python -m unittest discover .

lint: 
	poetry run python -m flake8

check: test lint
