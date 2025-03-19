
# TODO: Make these over-rideable
DOCKER_IMAGE_NAME=wfondrie/mokapot
DOCKER_IMAGE_TAG=latest

test:
	uv run --group test --extra xml python -m pytest --durations=0 --slow-last

testff:
	# Test but fails fast
	uv run --group test --extra xml python -m pytest --durations=0 --slow-last --last-failed -xs

profile:
	uv run --group test --extra xml --group profile scalene --cpu -m pytest

unit-test:
	uv run --group test --extra xml python -m pytest --durations=0 --slow-last -v ./tests/unit_tests

run-vignettes:
	cd docs/source/vignettes && for file in *.ipynb; do uv run --extra plot --group docs jupyter execute $${file}; done

clean-vignettes:
	cd docs/source/vignettes && for file in *.ipynb; do uv run --group docs jupyter nbconvert --clear-output --inplace $${file}; done

check: ruff-lint format pre-commit
	@echo "All checks passed"

build: build-wheel build-sdist build-docker
	@echo "Build completed"

build-wheel:
	uv run --with build python -m build --wheel .

build-sdist:
	uv run --with build python -m build --sdist .

build-docker:
	uv run --with build python -m build --wheel --outdir dist .
	docker build -t $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG) .
	docker run --rm $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG) mokapot --help

pre-commit:
	pre-commit run --all-files

ruff-lint:
	uv run ruff check .

lint-ci:
	uv run --no-project --with ruff ruff check . --output-format=github

format:
	uv run ruff format .

format-ci:
	uv run --no-project --with ruff ruff format --check .
