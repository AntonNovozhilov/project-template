PHOENIX_INDEX_URL := https://repository.rt.ru/repository/pypi-pypi.org/simple-allowed
PYTHON_VERSION ?= 3.13
export UV_DEFAULT_INDEX := $(PHOENIX_INDEX_URL)
export UV_PYTHON := $(PYTHON_VERSION)

.PHONY: all sync

all: sync

sync:
	uv lock --python $(PYTHON_VERSION)
	uv sync --locked --python $(PYTHON_VERSION)
