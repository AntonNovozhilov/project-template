PHOENIX_INDEX_URL := https://repository.rt.ru/repository/pypi-pypi.org/simple-allowed
export UV_DEFAULT_INDEX := $(PHOENIX_INDEX_URL)

.PHONY: all sync

all: sync

sync:
	uv lock
	uv sync --locked
