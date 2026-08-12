"""Заполняет значения, которые требуют безопасной сериализации."""

from __future__ import annotations

import json
import logging
from pathlib import Path


logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

GITFLAME_CI_PATH = Path(".gitflame-ci.yml")
README_PATH = Path("README.md")
DEPARTMENTS_PLACEHOLDER = "__CI_CD_DEPARTMENTS_JSON__"
COOKIECUTTER_PREFIX = "{" + "{ cookiecutter."
RAW_DEPARTMENTS = r"""{{ cookiecutter.CI_CD_DEPARTMENTS }}"""
README_REPLACEMENTS = {
    COOKIECUTTER_PREFIX + "project_name }}": {{ cookiecutter.project_name | tojson }},
    COOKIECUTTER_PREFIX + "CI_CD_DISPLAY_NAME }}": {{ cookiecutter.CI_CD_DISPLAY_NAME | tojson }},
    COOKIECUTTER_PREFIX + "CI_CD_DESCRIPTION }}": {{ cookiecutter.CI_CD_DESCRIPTION | tojson }},
    COOKIECUTTER_PREFIX + "CI_CD_AUTHOR }}": {{ cookiecutter.CI_CD_AUTHOR | tojson }},
}


def parse_departments(raw_departments: str) -> list[str]:
    """Разобрать строку отделов, введённую через запятую.

    Аргументы:
        raw_departments: Исходная строка из вопроса CI_CD_DEPARTMENTS.
    """
    return [
        department.strip()
        for department in raw_departments.split(",")
        if department.strip()
    ]


def render_departments_json(raw_departments: str) -> str:
    """Преобразовать строку отделов в JSON-массив.

    Аргументы:
        raw_departments: Исходная строка из вопроса CI_CD_DEPARTMENTS.
    """
    departments = parse_departments(raw_departments)
    return json.dumps(departments, ensure_ascii=False)


def replace_departments_placeholder(file_path: Path, departments_json: str) -> None:
    """Заменить маркер отделов в CI/CD-файле.

    Аргументы:
        file_path: Путь к файлу .gitflame-ci.yml в сгенерированном проекте.
        departments_json: JSON-массив отделов в виде строки.
    """
    try:
        source = file_path.read_text(encoding="utf-8")
        updated = source.replace(DEPARTMENTS_PLACEHOLDER, departments_json)
        file_path.write_text(updated, encoding="utf-8")
    except OSError:
        logger.exception("Не удалось обновить файл %s.", file_path)
        raise


def render_readme(file_path: Path) -> None:
    """Подставить метаданные проекта в README.

    Аргументы:
        file_path: Путь к README с метаданными сгенерированного проекта.
    """
    try:
        readme = file_path.read_text(encoding="utf-8")
        for placeholder, value in README_REPLACEMENTS.items():
            readme = readme.replace(placeholder, value)
        file_path.write_text(readme, encoding="utf-8")
    except OSError:
        logger.exception("Не удалось подставить метаданные в %s.", file_path)
        raise


def main() -> None:
    """Сериализовать отделы и обновить .gitflame-ci.yml."""
    departments_json = render_departments_json(RAW_DEPARTMENTS)
    replace_departments_placeholder(GITFLAME_CI_PATH, departments_json)
    render_readme(README_PATH)


if __name__ == "__main__":
    main()
