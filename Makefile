.PHONY: run install test lint clean seed help

run:
	ALLOW_INSECURE_HTTP=1 python3 app.py

install:
	pip install -r requirements.txt

test:
	ALLOW_INSECURE_HTTP=1 python3 -m pytest tests/ -v

test-fast:
	ALLOW_INSECURE_HTTP=1 python3 -m pytest tests/ -x -q

lint:
	python3 -m flake8 app.py utils/ config/ --max-line-length=100 --exclude=__pycache__

clean:
	find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null; true
	find . -name '*.pyc' -delete 2>/dev/null; true
	rm -f instance/todos.db

seed:
	ALLOW_INSECURE_HTTP=1 python3 scripts/seed_data.py

help:
	@echo "Available targets:"
	@echo "  run        Start the Flask dev server on port 5001"
	@echo "  install    Install Python dependencies"
	@echo "  test       Run the full test suite"
	@echo "  test-fast  Run tests, stop on first failure"
	@echo "  lint       Run flake8 linter"
	@echo "  clean      Remove __pycache__ and local DB"
	@echo "  seed       Populate the DB with sample todos"
