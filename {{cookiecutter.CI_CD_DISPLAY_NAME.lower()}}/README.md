# {{ cookiecutter.project_name }}

Номер заявки: `{{ cookiecutter.CI_CD_DISPLAY_NAME }}`

Описание: {{ cookiecutter.CI_CD_DESCRIPTION }}

Автор: `{{ cookiecutter.CI_CD_AUTHOR }}`

## Состав

- `.gitflame-ci.yml` — переменные для публикации в корпоративном контуре.
- `.python-version` — версия Python `3.13.3`.
- `pyproject.toml` и `uv.lock` — описание окружения для `uv`.
- `modules/main.py` — минимальная точка входа для будущего скрипта.
- `tests/test_main.py` — smoke-тест импорта.

## Локальная разработка

Установите зависимости отдельной командой:

```bash
uv sync
```

Запустите тесты:

```bash
uv run pytest
```

Запустите модуль:

```bash
uv run python -m modules.main
```

После переноса проекта в корпоративный контур настройки источника пакетов
должны применяться корпоративной средой. Этот шаблон не переключает индекс
пакетов самостоятельно.
