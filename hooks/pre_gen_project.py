"""Проверяет значения Cookiecutter до генерации проекта."""

from __future__ import annotations

import logging
import re
import sys


logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

MAX_TEXT_LENGTH = 255
DISPLAY_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
REPEATED_SEPARATOR_PATTERN = re.compile(r"[-_]{2,}")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


class CookiecutterValidationError(ValueError):
    """Ошибка проверки пользовательского ввода Cookiecutter."""


def validate_required_text(value: str, field_name: str) -> None:
    """Проверить обязательное текстовое поле.

    Аргументы:
        value: Значение поля после ввода в Cookiecutter.
        field_name: Имя поля для сообщения об ошибке.
    """
    if not value.strip():
        raise CookiecutterValidationError(f"{field_name}: значение обязательно.")


def validate_limited_text(value: str, field_name: str) -> None:
    """Проверить обязательное текстовое поле длиной до 255 символов.

    Аргументы:
        value: Значение поля после ввода в Cookiecutter.
        field_name: Имя поля для сообщения об ошибке.
    """
    validate_required_text(value, field_name)
    if len(value) > MAX_TEXT_LENGTH:
        raise CookiecutterValidationError(
            f"{field_name}: длина должна быть не больше {MAX_TEXT_LENGTH} символов."
        )


def validate_display_name(value: str) -> None:
    """Проверить номер заявки для технического имени проекта.

    Аргументы:
        value: Номер заявки, например ACDUU-490.
    """
    validate_limited_text(value, "CI_CD_DISPLAY_NAME")
    if not DISPLAY_NAME_PATTERN.fullmatch(value):
        raise CookiecutterValidationError(
            "CI_CD_DISPLAY_NAME: разрешены только латинские буквы, цифры, '-' и '_'."
        )
    if value[0] in "-_" or value[-1] in "-_":
        raise CookiecutterValidationError(
            "CI_CD_DISPLAY_NAME: '-' и '_' не могут быть первым или последним символом."
        )
    if REPEATED_SEPARATOR_PATTERN.search(value):
        raise CookiecutterValidationError(
            "CI_CD_DISPLAY_NAME: разделители '-' и '_' не должны повторяться подряд."
        )


def validate_email(value: str) -> None:
    """Проверить общий формат e-mail.

    Аргументы:
        value: E-mail автора проекта.
    """
    validate_limited_text(value, "CI_CD_AUTHOR")
    if not EMAIL_PATTERN.fullmatch(value):
        raise CookiecutterValidationError(
            "CI_CD_AUTHOR: укажите e-mail в формате name@example.com."
        )


def validate_version(value: str) -> None:
    """Проверить версию проекта в формате SemVer.

    Аргументы:
        value: Версия проекта, например `1.0.0` или `1.0.0-rc.1`.
    """
    validate_limited_text(value, "version")
    if not SEMVER_PATTERN.fullmatch(value):
        raise CookiecutterValidationError(
            "version: укажите SemVer-версию в формате 1.0.0 или 1.0.0-rc.1."
        )


def validate_cookiecutter_context() -> None:
    """Проверить все значения, которые вводит пользователь."""
    validate_display_name("{{ cookiecutter.CI_CD_DISPLAY_NAME }}")
    validate_limited_text("{{ cookiecutter.project_name }}", "project_name")
    validate_version("{{ cookiecutter.version }}")
    validate_email("{{ cookiecutter.CI_CD_AUTHOR }}")
    validate_limited_text("{{ cookiecutter.CI_CD_DESCRIPTION }}", "CI_CD_DESCRIPTION")


def main() -> int:
    """Запустить проверку и вернуть код завершения для Cookiecutter."""
    try:
        validate_cookiecutter_context()
    except CookiecutterValidationError as error:
        logger.error("%s Повторите команду cookiecutter с корректным значением.", error)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
