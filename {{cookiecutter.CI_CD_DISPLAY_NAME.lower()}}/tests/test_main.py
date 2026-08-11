"""Smoke-тесты стартовой структуры проекта."""

from __future__ import annotations

import errno
import importlib
from pathlib import Path
from types import ModuleType

import pytest

from modules.domain.exceptions import (
    ApplicationError,
    AssetsDestinationWritePermissionError,
    AssetsDiskSpaceError,
    AssetsSourceNotDirectoryError,
    AssetsSourceNotFoundError,
    AssetsSourceReadPermissionError,
    InputDataError,
)
from modules.main import main
from modules.settings import paths as paths_module
from modules.settings.paths import AppPaths, validate_assets_destination, validate_assets_source


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_ROOT = PROJECT_ROOT / "modules"


def get_package_paths() -> list[Path]:
    """Найти Python-пакеты внутри `modules`."""
    return sorted(init_file.parent for init_file in MODULES_ROOT.rglob("__init__.py"))


def import_entrypoint_module() -> ModuleType:
    """Импортировать модуль основной точки входа."""
    return importlib.import_module("modules.main")


def test_main_module_imports() -> None:
    """Проверить, что основная точка входа импортируется без побочных ошибок."""
    module = import_entrypoint_module()

    assert module.__name__ == "modules.main"


def test_runtime_directories_and_assets_are_prepared(tmp_path: Path) -> None:
    """Проверить создание runtime-каталогов и рекурсивное копирование ресурсов."""
    paths = AppPaths(root=tmp_path / ".rpa")

    result = main(paths)

    assert result == 0
    assert paths.config_dir.is_dir()
    assert paths.share_dir.is_dir()
    assert paths.state_dir.is_dir()
    assert paths.assets_dir.is_dir()
    assert (paths.assets_dir / ".gitkeep").is_file()
    assert list((paths.state_dir / "logs").glob("*.log"))


def test_input_data_error_is_application_error() -> None:
    """Проверить общую иерархию ожидаемых ошибок приложения."""
    error = InputDataError("Некорректный входной файл")

    assert isinstance(error, ApplicationError)


def test_missing_assets_source_is_reported(tmp_path: Path) -> None:
    """Проверить понятную ошибку, когда исходный каталог resources отсутствует."""
    source_dir = tmp_path / "missing-assets"

    with pytest.raises(AssetsSourceNotFoundError):
        validate_assets_source(source_dir)


def test_assets_source_file_is_reported(tmp_path: Path) -> None:
    """Проверить понятную ошибку, когда источник ресурсов является файлом."""
    source_file = tmp_path / "assets.txt"
    source_file.write_text("данные", encoding="utf-8")

    with pytest.raises(AssetsSourceNotDirectoryError):
        validate_assets_source(source_file)


def test_assets_source_read_permission_is_reported(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Проверить понятную ошибку, когда нельзя читать каталог поставляемых ресурсов."""
    source_dir = tmp_path / "assets"
    source_dir.mkdir()
    monkeypatch.setattr(paths_module.os, "access", deny_directory_access)

    with pytest.raises(AssetsSourceReadPermissionError):
        validate_assets_source(source_dir)


def test_assets_destination_write_permission_is_reported(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Проверить понятную ошибку, когда нельзя записать runtime-ресурсы."""
    destination_dir = tmp_path / ".rpa" / "assets"
    destination_dir.mkdir(parents=True)
    monkeypatch.setattr(paths_module.os, "access", deny_directory_access)

    with pytest.raises(AssetsDestinationWritePermissionError):
        validate_assets_destination(destination_dir)


def test_disk_space_error_is_reported(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Проверить понятную ошибку, когда диск заполняется во время копирования."""
    paths = AppPaths(root=tmp_path / ".rpa")
    paths.ensure_directories()
    monkeypatch.setattr(paths_module.shutil, "copytree", raise_disk_space_error)

    with pytest.raises(AssetsDiskSpaceError):
        paths.copy_packaged_assets()


def deny_directory_access(path: Path, mode: int) -> bool:
    """Вернуть отказ в доступе для проверки диагностических ошибок.

    Аргументы:
        path: Проверяемый каталог.
        mode: Требуемый режим доступа.
    """
    return False


def raise_disk_space_error(*args: object, **kwargs: object) -> None:
    """Сымитировать системную ошибку нехватки места для проверки обработки.

    Аргументы:
        args: Позиционные аргументы функции копирования.
        kwargs: Именованные аргументы функции копирования.
    """
    raise OSError(errno.ENOSPC, "No space left on device")


def test_each_python_package_has_agent_manifest() -> None:
    """Проверить, что каждый Python-пакет содержит манифест для агента."""
    missing_manifests = [
        str(package_path.relative_to(PROJECT_ROOT))
        for package_path in get_package_paths()
        if not (package_path / "AGENTS.md").is_file()
    ]

    assert missing_manifests == []
