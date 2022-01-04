export PYTHONPATH := src:$(PYTHONPATH)
GIT_COMMIT = $(shell git rev-parse --short HEAD)

.DEFAULT_GOAL = help

.PHONY: archive
archive: clean ## Archive the project using git archive.
	git archive --format=zip --output=pycli.zip "$(GIT_COMMIT)"

.PHONY: build
build:  ## Build the package, as a tarball and a wheel.
	poetry build

.PHONY: clean
clean:  ## Clean up all types of project builds and cache files
	@rm -rf build/ dist/ *.egg-info *.spec src/*.spec ; \
	rm -rf site/ ; \
	rm docs/index.md ; \
	rm -rf .coverage .pytest_cache/ htmlcov/ .tox/ .mypy_cache/ ; \
	rm -rf __pycache__/ ; \
	find tests src/pycli -type d -name "__pycache__" -exec rm -rf {} + ; \
	find tests src/pycli -type f -name "*.pyc" -exec rm -rf {} + ;

.PHONY: docs
docs:  ## Build the project's documentation.
	python docs/build.py ; \
	mkdocs build ;

.PHONY: docs-serve
docs-serve: docs  ## Build and the serve the project's documentation.
	mkdocs serve

.PHONY: format
format:  ## Format the project's code.
	autoflake --remove-all-unused-imports --recursive --in-place --exclude=__init__.py src/pycli tests ; \
	black src/pycli tests ; \
	isort src/pycli tests ;

.PHONY: help
help:  ## Print this message and exit.
	@IFS=$$'\n' ; \
	help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/:/'`); \
	printf "%-30s %s\n" "target" "help" ; \
	printf "%-30s %s\n" "------" "----" ; \
	for help_line in $${help_lines[@]}; do \
		IFS=$$':' ; \
		help_split=($$help_line) ; \
		help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		printf '\033[36m'; \
		printf "%-30s %s" $$help_command ; \
		printf '\033[0m'; \
		printf "%s\n" $$help_info; \
	done

.PHONY: lint
lint:  ## Apply linting and formatting to the project's code.
	pylint src/pycli

.PHONY: test
test: clean  ## Run tests using pytest.
	pytest

.PHONY: test-tox
test-tox: clean  ## Run tests over multiple versions using tox.
	tox

.PHONY: test-examples
test-examples: clean  ## Run quick test for example files
	@find examples -type f -name '*.py' | xargs -I'{}' sh -c 'python {} --help >/dev/null 2>&1 || (echo "{} failed")'

.PHONY: test-all
test-all: test test-examples  ## Run tests on the regular test suite and for examples.
