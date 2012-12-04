# Copyright (C) 2010-2012 Taras Marchuk
SHELL=/bin/bash
PROJECT_NAME=advanced-01
PROJECT_DIR=./
PYTHON=python
TESTS_DIR=tests

clean:
	@echo Cleaning up...
	@find $(PROJECT_DIR) -name '*~*' -exec rm {} \;
	@find $(PROJECT_DIR) -name '*.pyc' -exec rm {} \;
	@echo Done

test:
	@$(PYTHON) -m unittest $(TESTS_DIR)
