#!/usr/bin/make -f

PYTHON=python3
PKGNAME=s1isp

.PHONY: default help dist check fullcheck coverage lint api docs clean cleaner distclean

default: help

help:
	@echo "Usage: make <TARGET>"
	@echo "Available targets:"
	@echo "  help      - print this help message"
	@echo "  dist      - generate the distribution packages (source and wheel)"
	@echo "  check     - run a full test (using pytest)"
	@echo "  fullcheck - run a full test (using tox)"
	@echo "  coverage  - run tests and generate the coverage report"
	@echo "  lint      - perform check with code linter (flake8, black)"
	@echo "  api       - update the API source files in the documentation"
	@echo "  docs      - generate the sphinx documentation"
	@echo "  clean     - clean build artifacts"
	@echo "  cleaner   - clean cache files and working directories of al tools"
	@echo "  distclean - clean all the generated files"

dist:
	$(PYTHON) -m build
	$(PYTHON) -m twine check dist/*

check:
	$(PYTHON) -m pytest

fullcheck:
	$(PYTHON) -m tox

coverage:
	$(PYTHON) -m pytest --cov=$(PKGNAME) --cov-report=html --cov-report=term

lint:
	$(PYTHON) -m flake8 --count --statistics $(PKGNAME)
	$(PYTHON) -m pydocstyle --count $(PKGNAME)
	$(PYTHON) -m isort --check $(PKGNAME)
	$(PYTHON) -m black --check $(PKGNAME)

api:
	$(RM) -r docs/api
	sphinx-apidoc --module-first --separate --no-toc -o docs/api \
	  --doc-project "$(PKGNAME) API" --templatedir docs/_templates/apidoc \
	  $(PKGNAME)

docs:
	$(MAKE) -C docs html


clean:
	$(RM) -r *.egg-info build
	find . -name __pycache__ -type d -exec $(RM) -r {} +
	# $(RM) -r __pycache__ */__pycache__ */*/__pycache__ */*/tests/__pycache__
	# $(MAKE) -C docs clean
	$(RM) -r docs/_build


cleaner: clean
	$(RM) -r .coverage htmlcov .pytest_cache .tox .ipynb_checkpoints


distclean: cleaner
	$(RM) -r dist

