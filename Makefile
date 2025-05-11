#!/usr/bin/make -f

PYTHON=python3
SPHINX_APIDOC=sphinx-apidoc
TARGET=s1isp

.PHONY: default help dist check fullcheck coverage clean cleaner distclean \
        lint docs api ext

default: help

help:
	@echo "Usage: make <TARGET>"
	@echo "Available targets:"
	@echo "  help      - print this help message"
	@echo "  dist      - generate the distribution packages (source and wheel)"
	@echo "  check     - run a full test (using pytest)"
	@echo "  fullcheck - run a full test (using tox)"
	@echo "  coverage  - run tests and generate the coverage report"
	@echo "  clean     - clean build artifacts"
	@echo "  cleaner   - clean cache files and working directories of al tools"
	@echo "  distclean - clean all the generated files"
	@echo "  lint      - perform check with code linter (flake8, black)"
	@echo "  docs      - generate the sphinx documentation"
	@echo "  api       - update the API source files in the documentation"
	@echo "  ext       - build Python extensions in-place"

dist:
	$(PYTHON) -m build
	$(PYTHON) -m twine check dist/*.tar.gz dist/*.whl

check: ext
	# $(PYTHON) -m pytest --doctest-modules $(TARGET) tests
	$(PYTHON) -m pytest $(TARGET) tests

fullcheck:
	$(PYTHON) -m tox run

coverage: ext
	# $(PYTHON) -m pytest --doctest-modules --cov=$(TARGET) --cov-report=html --cov-report=term $(TARGET) tests
	$(PYTHON) -m pytest --cov=$(TARGET) --cov-report=html --cov-report=term $(TARGET) tests

clean:
	$(RM) -r *.*-info build
	find . -name __pycache__ -type d -exec $(RM) -r {} +
	# $(RM) -r __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__
	$(RM) $(TARGET)/_*.c $(TARGET)/*.so $(TARGET)/*.o
	if [ -f docs/Makefile ] ; then $(MAKE) -C docs clean; fi
	$(RM) -r docs/_build

cleaner: clean
	$(RM) -r .coverage htmlcov
	$(RM) -r .pytest_cache
	$(RM) -r .tox
	$(RM) -r .mypy_cache
	$(RM) -r .ruff_cache
	$(RM) -r .ipynb_checkpoints

distclean: cleaner
	$(RM) -r dist

lint:
	$(PYTHON) -m flake8 --count --statistics $(TARGET) tests
	$(PYTHON) -m pydocstyle --count $(TARGET)
	$(PYTHON) -m isort --check $(TARGET) tests
	$(PYTHON) -m black --check $(TARGET) tests
	# $(PYTHON) -m mypy --check-untyped-defs --ignore-missing-imports $(TARGET)
	ruff check $(TARGET)
	codespell

docs: ext
	mkdir -p docs/_static
	$(MAKE) -C docs PYTHONPATH=.. html
	$(MAKE) -C docs PYTHONPATH=.. linkcheck
	$(MAKE) -C docs PYTHONPATH=.. spelling

api:
	$(RM) -r docs/api
	$(SPHINX_APIDOC) --module-first --separate --no-toc -o docs/api \
	  --doc-project "$(TARGET) API" --templatedir docs/_templates/apidoc \
	  $(TARGET) $(TARGET)/tests

ext:
	$(PYTHON) setup.py build_ext --inplace
