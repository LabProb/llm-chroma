# list of targets
.PHONY: init venv activate install install-dev lint format test coverage clean check run help

# variables for the virtual environment
PYTHON				?= python3
VENV						?= .venv
PIP							= $(VENV)/bin/pip

## init: create venv and install prod+dev dependencies
init: venv install-dev		## create virtual environment and install packages

## venv: create .venv folder if it doesn’t exist yet
venv:		## create virtual environment
				@test -d $(VENV) || $(PYTHON) -m venv $(VENV)

activate: venv ## activate virtual environment
	@. $(VENV)/bin/activate; exec $$SHELL

## install only production dependencies
install: venv		## install production dependencies
				@echo "⏳ Installing production requirements…"
				@$(PIP) install --upgrade pip
				@$(PIP) install -r requirements.txt

## install-dev: production + development
install-dev: venv		## install production and development dependencies
				@echo "⏳ Installing all requirements…"
				@$(PIP) install --upgrade pip
				@$(PIP) install -r requirements.txt
				@$(PIP) install -r requirements-dev.txt

## lint: code style check with Ruff
lint: venv		## запустити Ruff lint
				@$(VENV)/bin/ruff check app tests

## format: autoformat with Ruff
format: venv		## autoformat code using Ruff
				@$(VENV)/bin/ruff check app tests --fix

## test: run pytest
test: venv		## run tests
				@$(VENV)/bin/pytest tests

## coverage: tests + coverage report
coverage: venv		## run tests with coverage
				@$(VENV)/bin/coverage run -m pytest
				@$(VENV)/bin/coverage report -m

## check: lint + tests + coverage
check: lint test coverage		## full check (lint, test, coverage)

## run: start Uvicorn server
run: init		## run FastAPI with autoreload
				@echo "🚀 Starting Uvicorn..."
				@$(VENV)/bin/uvicorn app.main:app --reload

clean:  ## remove caches, reports, and __init__.py (does not touch venv)
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type f -name '__init__.py' -delete
	rm -f .coverage

clean-venv:	## remove only the virtual environment
	rm -rf $(VENV)

distclean: clean clean-venv	## повністю очистити проект

## help: show targets with descriptions
help:		## display Makefile help
				@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
				awk 'BEGIN {FS = ":.*?## "}; {printf "		\033[36m%-15s\033[0m %s\n", $$1, $$2}'
