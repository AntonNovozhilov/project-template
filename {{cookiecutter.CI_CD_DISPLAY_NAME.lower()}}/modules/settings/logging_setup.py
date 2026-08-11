"""Настраивает единое консольное и файловое логирование приложения."""

from __future__ import annotations

from datetime import datetime
import logging
import logging.config
import os
from pathlib import Path


DEFAULT_KEEP_RUNS = 5
DEFAULT_MAX_BYTES = 5 * 1024 * 1024
DEFAULT_BACKUP_COUNT = 1


def setup_logging(
    app_name: str,
    logger_name: str,
    log_dir: Path,
    keep_runs: int = DEFAULT_KEEP_RUNS,
) -> Path:
    """Настроить логирование и вернуть путь к основному файлу текущего запуска.

    Аргументы:
        app_name: Техническое имя приложения для имени файла журнала.
        logger_name: Имя корневого логгера прикладного кода.
        log_dir: Каталог, куда записываются журналы запусков.
        keep_runs: Число последних запусков, которые нужно сохранить.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    cleanup_old_runs(log_dir, app_name, max(keep_runs - 1, 0))
    log_file = create_log_file_path(log_dir, app_name)
    logging.config.dictConfig(build_logging_config(log_file, logger_name))
    logging.captureWarnings(True)
    return log_file


def create_log_file_path(log_dir: Path, app_name: str) -> Path:
    """Сформировать путь к файлу журнала одного запуска.

    Аргументы:
        log_dir: Каталог файлов журналов.
        app_name: Техническое имя приложения.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return log_dir / f"{app_name}_{timestamp}_{os.getpid()}.log"


def build_logging_config(log_file: Path, logger_name: str) -> dict[str, object]:
    """Собрать конфигурацию для консольного и файлового журналов.

    Аргументы:
        log_file: Путь к создаваемому файлу журнала.
        logger_name: Имя прикладного логгера.
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {"format": "%(levelname)s: %(message)s"},
            "file": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | "
                "%(filename)s:%(lineno)d | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "console",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "file",
                "filename": str(log_file),
                "encoding": "utf-8",
                "maxBytes": DEFAULT_MAX_BYTES,
                "backupCount": DEFAULT_BACKUP_COUNT,
            },
        },
        "root": {"level": "WARNING", "handlers": ["console", "file"]},
        "loggers": {
            logger_name: {
                "level": "DEBUG",
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
    }


def cleanup_old_runs(log_dir: Path, app_name: str, keep_previous: int) -> None:
    """Удалить журналы запусков, не входящие в заданное число последних.

    Аргументы:
        log_dir: Каталог файлов журналов.
        app_name: Техническое имя приложения.
        keep_previous: Число прошлых запусков, которые нужно сохранить.
    """
    run_files = sorted(
        log_dir.glob(f"{app_name}_*.log"),
        key=get_file_modification_time,
        reverse=True,
    )
    for log_file in run_files[keep_previous:]:
        remove_log_file_set(log_file)


def get_file_modification_time(file_path: Path) -> float:
    """Вернуть время изменения файла журнала.

    Аргументы:
        file_path: Путь к файлу журнала.
    """
    return file_path.stat().st_mtime


def remove_log_file_set(log_file: Path) -> None:
    """Удалить основной журнал и его файлы ротации.

    Аргументы:
        log_file: Путь к основному файлу журнала.
    """
    for candidate in (log_file, *log_file.parent.glob(f"{log_file.name}.*")):
        try:
            candidate.unlink(missing_ok=True)
        except OSError:
            logging.getLogger(__name__).exception("Не удалось удалить журнал %s.", candidate)
