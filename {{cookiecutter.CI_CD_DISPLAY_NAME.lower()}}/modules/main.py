"""Запускает общий runtime-сценарий приложения."""

from __future__ import annotations

import logging

from modules.domain.exceptions import ApplicationError
from modules.settings.logging_setup import setup_logging
from modules.settings.paths import AppPaths


APP_NAME = "{{ cookiecutter.CI_CD_DISPLAY_NAME.lower().replace('-', '_') }}"
LOGGER_NAME = "modules"

logger = logging.getLogger(LOGGER_NAME)


def main(paths: AppPaths | None = None) -> int:
    """Подготовить runtime-каталоги, синхронизировать ресурсы и запустить сценарий.

    Аргументы:
        paths: Пути runtime-каталогов или `None` для стандартного `~/.rpa`.
    """
    app_paths = paths or AppPaths()
    app_paths.ensure_directories()
    log_file = setup_logging(APP_NAME, LOGGER_NAME, app_paths.state_dir / "logs")
    logger.info("Запуск приложения")
    logger.info("Логгер инициализирован: %s", log_file)

    try:
        app_paths.copy_packaged_assets()
        logger.info("Ресурсы скопированы в %s", app_paths.assets_dir)
        return run()
    except KeyboardInterrupt:
        logger.warning("Выполнение прервано пользователем")
        return 130
    except ApplicationError as error:
        logger.error("%s", error)
        return 2
    except Exception:
        logger.exception("Необработанная ошибка приложения")
        return 1
    finally:
        logger.info("Завершение приложения")


def run() -> int:
    """Вернуть код успешного выполнения пустого стартового сценария."""
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
