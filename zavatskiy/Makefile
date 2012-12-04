PROJECT_NAME=advanced-01
ENV=~/.virtualenvs/advanced-01
PYTHON=$(ENV)/bin/python
PIP=$(ENV)/bin/pip

default:
	virtualenv requirements run

run:
	@$(PYTHON) server01.py 

test:
	@$(PYTHON) tests/test_client01.py

virtualenv:
	@echo "Creating virtual environment within $(ENV) directory"
	@virtualenv -q $(ENV)

requirements:
	@echo "Installing requirements"
	@$(PIP) install -qr requirements.txt

clean:
	@echo "Cleaning *.pyc files"
	@find . -name "*.pyc" -exec rm -f {} \;
