"""Определяет runtime-каталоги и переносит поставляемые ресурсы."""

from __future__ import annotations

from dataclasses import dataclass, field
import errno
import os
from pathlib import Path
import shutil

from modules.domain.exceptions import (
    AssetsDestinationWritePermissionError,
    AssetsDiskSpaceError,
    AssetsSourceNotDirectoryError,
    AssetsSourceNotFoundError,
    AssetsSourceReadPermissionError,
    AssetsSynchronizationError,
)


RPA_DIRECTORY_NAME = ".rpa"
ASSETS_DIRECTORY_NAME = "assets"


@dataclass(frozen=True)
class AppPaths:
    """Хранит пути к runtime-каталогам приложения в домашнем каталоге.

    Аргументы:
        root: Корневой каталог runtime-данных. По умолчанию `~/.rpa`.
    """

    root: Path = field(default_factory=lambda: Path.home() / RPA_DIRECTORY_NAME)

    config_dir: Path = field(init=False)
    share_dir: Path = field(init=False)
    state_dir: Path = field(init=False)
    assets_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        """Вычислить дочерние runtime-каталоги."""
        object.__setattr__(self, "config_dir", self.root / "config")
        object.__setattr__(self, "share_dir", self.root / "share")
        object.__setattr__(self, "state_dir", self.root / "state")
        object.__setattr__(self, "assets_dir", self.root / ASSETS_DIRECTORY_NAME)

    def ensure_directories(self) -> AppPaths:
        """Создать все runtime-каталоги, если они ещё отсутствуют."""
        for directory in (
            self.config_dir,
            self.share_dir,
            self.state_dir,
            self.assets_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)
        return self

    def copy_packaged_assets(self) -> None:
        """Рекурсивно скопировать поставляемые ресурсы в runtime-каталог."""
        source_dir = get_packaged_assets_directory()
        validate_assets_source(source_dir)
        validate_assets_destination(self.assets_dir)
        try:
            shutil.copytree(source_dir, self.assets_dir, dirs_exist_ok=True)
        except OSError as error:
            raise build_assets_synchronization_error(source_dir, self.assets_dir, error) from error
        except shutil.Error as error:
            raise AssetsSynchronizationError(
                f"Не удалось скопировать ресурсы из {source_dir} в {self.assets_dir}: {error}."
            ) from error


def get_packaged_assets_directory() -> Path:
    """Вернуть каталог `modules/assets`, поставляемый вместе с приложением."""
    return Path(__file__).resolve().parents[1] / ASSETS_DIRECTORY_NAME


def validate_assets_source(source_dir: Path) -> None:
    """Проверить наличие, тип и права чтения каталога поставляемых ресурсов.

    Аргументы:
        source_dir: Каталог `modules/assets`, который должен быть скопирован.
    """
    if not source_dir.exists():
        raise AssetsSourceNotFoundError(f"Исходный каталог ресурсов не найден: {source_dir}.")
    if not source_dir.is_dir():
        raise AssetsSourceNotDirectoryError(
            f"Источник ресурсов существует, но не является каталогом: {source_dir}."
        )
    if not os.access(source_dir, os.R_OK | os.X_OK):
        raise AssetsSourceReadPermissionError(
            f"Нет прав на чтение исходного каталога ресурсов: {source_dir}."
        )


def validate_assets_destination(destination_dir: Path) -> None:
    """Проверить права записи в runtime-каталог ресурсов.

    Аргументы:
        destination_dir: Каталог `~/.rpa/assets`, куда копируются ресурсы.
    """
    existing_directory = get_existing_parent_directory(destination_dir)
    if not os.access(existing_directory, os.W_OK | os.X_OK):
        raise AssetsDestinationWritePermissionError(
            f"Нет прав на запись в каталог ресурсов: {destination_dir}."
        )


def get_existing_parent_directory(directory: Path) -> Path:
    """Найти ближайший существующий каталог для проверки прав записи.

    Аргументы:
        directory: Каталог, который может ещё не существовать.
    """
    candidate = directory
    while not candidate.exists():
        candidate = candidate.parent
    return candidate


def build_assets_synchronization_error(
    source_dir: Path,
    destination_dir: Path,
    error: OSError,
) -> AssetsSynchronizationError:
    """Преобразовать системную ошибку копирования в ожидаемую ошибку приложения.

    Аргументы:
        source_dir: Каталог, из которого копируются ресурсы.
        destination_dir: Каталог, куда копируются ресурсы.
        error: Системная ошибка операции копирования.
    """
    if error.errno == errno.ENOSPC:
        return AssetsDiskSpaceError(
            f"Недостаточно места на диске для копирования ресурсов в {destination_dir}."
        )
    if error.errno in {errno.EACCES, errno.EPERM}:
        return AssetsDestinationWritePermissionError(
            f"Нет прав на запись в каталог ресурсов: {destination_dir}."
        )
    return AssetsSynchronizationError(
        f"Не удалось скопировать ресурсы из {source_dir} в {destination_dir}: {error}."
    )
