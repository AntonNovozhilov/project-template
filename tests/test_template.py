"""Тесты Cookiecutter-шаблона проекта."""

from __future__ import annotations

import os
import json
import subprocess
from pathlib import Path

import pytest


TEMPLATE_ROOT = Path(__file__).resolve().parents[1]
COOKIECUTTER_PYTHON = os.environ.get("COOKIECUTTER_PYTHON", "python3")
BASE_CONTEXT = {
    "CI_CD_DISPLAY_NAME": "ACDUU-490",
    "project_name": "Тестовая автоматизация",
    "CI_CD_AUTHOR": "ivan.ivanov@example.com",
    "CI_CD_DEPARTMENTS": "Отдел 1, Группа 2",
    "CI_CD_DESCRIPTION": "Описание тестовой автоматизации",
}
REQUIRED_FILES = {
    ".gitflame-ci.yml",
    ".gitignore",
    ".python-version",
    "README.md",
    "pyproject.toml",
    "uv.lock",
    "modules/__init__.py",
    "modules/main.py",
    "tests/test_main.py",
}


def run_cookiecutter(output_dir: Path, context: dict[str, str]) -> subprocess.CompletedProcess[str]:
    """Запустить Cookiecutter с тестовым контекстом.

    Аргументы:
        output_dir: Временный каталог, куда должен быть создан проект.
        context: Значения Cookiecutter для неинтерактивной генерации.
    """
    config_path = output_dir / "cookiecutter-config.yaml"
    replay_dir = output_dir / "replay"
    output_dir.mkdir(parents=True, exist_ok=True)
    replay_dir.mkdir(parents=True, exist_ok=True)
    config_path.write_text(f"replay_dir: {replay_dir}\n", encoding="utf-8")

    command = [
        COOKIECUTTER_PYTHON,
        "-m",
        "cookiecutter",
        str(TEMPLATE_ROOT),
        "--no-input",
        "--config-file",
        str(config_path),
        "--output-dir",
        str(output_dir),
    ]
    for key, value in context.items():
        command.append(f"{key}={value}")

    return subprocess.run(
        command,
        check=False,
        cwd=TEMPLATE_ROOT,
        env={**os.environ, "PYTHONUTF8": "1"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def assert_valid_generation(project_dir: Path) -> None:
    """Проверить обязательные файлы и структуру сгенерированного проекта.

    Аргументы:
        project_dir: Каталог сгенерированного проекта.
    """
    missing_files = [
        relative_path
        for relative_path in REQUIRED_FILES
        if not (project_dir / relative_path).exists()
    ]
    assert missing_files == []
    assert not (project_dir / ".git").exists()
    assert (project_dir / ".python-version").read_text(encoding="utf-8") == "3.13.3\n"


def test_template_generates_expected_project(tmp_path: Path) -> None:
    """Проверить успешную генерацию с обычным списком отделов."""
    # preparation
    output_dir = tmp_path / "generated"

    # action
    result = run_cookiecutter(output_dir, BASE_CONTEXT)

    # assertion
    assert result.returncode == 0, result.stderr
    project_dir = output_dir / "acduu-490"
    assert_valid_generation(project_dir)
    gitflame_ci = (project_dir / ".gitflame-ci.yml").read_text(encoding="utf-8")
    assert 'CI_CD_DISPLAY_NAME: "ACDUU-490"' in gitflame_ci
    assert 'CI_CD_AUTHOR: "ivan.ivanov@example.com"' in gitflame_ci
    assert "CI_CD_DEPARTMENTS: '[\"Отдел 1\", \"Группа 2\"]'" in gitflame_ci
    assert 'CI_CD_DESCRIPTION: "Описание тестовой автоматизации"' in gitflame_ci
    assert "scriptplatform-scripts-test/repo-build" in gitflame_ci

    pyproject = (project_dir / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "acduu-490"' in pyproject
    assert 'description = "Описание тестовой автоматизации"' in pyproject
    assert 'requires-python = ">=3.13,<3.14"' in pyproject
    assert 'dependencies = []' in pyproject
    assert '"pytest>=8.0.0"' in pyproject
    assert 'pythonpath = ["."]' in pyproject


def test_template_generates_empty_departments(tmp_path: Path) -> None:
    """Проверить, что пустой ввод отделов превращается в JSON-массив."""
    # preparation
    output_dir = tmp_path / "generated"
    context = {**BASE_CONTEXT, "CI_CD_DEPARTMENTS": ""}

    # action
    result = run_cookiecutter(output_dir, context)

    # assertion
    assert result.returncode == 0, result.stderr
    gitflame_ci = (output_dir / "acduu-490" / ".gitflame-ci.yml").read_text(
        encoding="utf-8"
    )
    assert "CI_CD_DEPARTMENTS: '[]'" in gitflame_ci


def test_template_escapes_quoted_departments(tmp_path: Path) -> None:
    """Проверить, что кавычки и кириллица в отделах не ломают JSON в YAML."""
    # preparation
    output_dir = tmp_path / "generated"
    context = {**BASE_CONTEXT, "CI_CD_DEPARTMENTS": 'Отдел "А", Управление'}

    # action
    result = run_cookiecutter(output_dir, context)

    # assertion
    assert result.returncode == 0, result.stderr
    gitflame_ci = (output_dir / "acduu-490" / ".gitflame-ci.yml").read_text(
        encoding="utf-8"
    )
    assert "CI_CD_DEPARTMENTS: '[\"Отдел \\\"А\\\"\", \"Управление\"]'" in gitflame_ci


@pytest.mark.parametrize(
    "display_name",
    ["ACDUU/490", "-ACDUU-490", "ACDUU-490-", "ACDUU--490", "ACDUU__490"],
)
def test_template_rejects_invalid_display_name(
    tmp_path: Path,
    display_name: str,
) -> None:
    """Проверить отказ при недопустимом техническом номере заявки."""
    # preparation
    output_dir = tmp_path / "generated"
    context = {**BASE_CONTEXT, "CI_CD_DISPLAY_NAME": display_name}

    # action
    result = run_cookiecutter(output_dir, context)

    # assertion
    assert result.returncode != 0
    assert "CI_CD_DISPLAY_NAME" in result.stderr


def test_template_rejects_invalid_email(tmp_path: Path) -> None:
    """Проверить отказ при некорректном формате e-mail автора."""
    # preparation
    output_dir = tmp_path / "generated"
    context = {**BASE_CONTEXT, "CI_CD_AUTHOR": "invalid-email"}

    # action
    result = run_cookiecutter(output_dir, context)

    # assertion
    assert result.returncode != 0
    assert "CI_CD_AUTHOR" in result.stderr


def test_root_readme_contains_required_guidance() -> None:
    """Проверить, что README шаблона содержит обязательные инструкции."""
    # preparation
    readme_path = TEMPLATE_ROOT / "README.md"

    # action
    readme = readme_path.read_text(encoding="utf-8")
    line_count = len(readme.splitlines())

    # assertion
    assert 120 <= line_count <= 180
    for required_text in [
        "python -m pip --version",
        "python -m ensurepip --upgrade",
        "Cookiecutter",
        "uv sync",
        "uv add",
        "uv remove",
        "uv lock",
        "uv run pytest",
        "Феникс",
        "GitHub URL или путь",
    ]:
        assert required_text in readme


def test_cookiecutter_uses_human_readable_prompts() -> None:
    """Проверить, что интерактивные вопросы не показывают технические имена."""
    # preparation
    cookiecutter_config_path = TEMPLATE_ROOT / "cookiecutter.json"

    # action
    cookiecutter_config = json.loads(
        cookiecutter_config_path.read_text(encoding="utf-8")
    )
    prompts = cookiecutter_config["__prompts__"]

    # assertion
    assert prompts == {
        "CI_CD_DISPLAY_NAME": "Введите номер заявки, например ACDUU-490",
        "project_name": "Введите понятное название автоматизации",
        "CI_CD_AUTHOR": "Введите e-mail автора",
        "CI_CD_DEPARTMENTS": "Введите отделы через запятую или оставьте пустым",
        "CI_CD_DESCRIPTION": "Введите краткое описание автоматизации",
    }
