"""Smoke-тесты минимальной структуры проекта."""

from __future__ import annotations

import importlib
from types import ModuleType


def test_main_module_imports() -> None:
    """Проверить, что точка входа импортируется без побочных ошибок."""
    # preparation
    module_name = "modules.main"

    # action
    module = importlib.import_module(module_name)

    # assertion
    assert isinstance(module, ModuleType)
