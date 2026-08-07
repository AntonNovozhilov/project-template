# Шаблон Python-скрипта для ScriptHub

Этот репозиторий содержит публичный Cookiecutter-шаблон для создания проекта
вне корпоративного контура. Сгенерированный проект можно разрабатывать локально,
а потом перенести внутрь компании и создать там обычный GitLab-репозиторий.

Шаблон не создаёт удалённый репозиторий, не делает `git push`, не создаёт `.git`
в результате и не устанавливает зависимости автоматически. Установка выполняется
отдельно командой `uv sync`.

## Что будет создано

Имя каталога берётся из `CI_CD_DISPLAY_NAME` и приводится к нижнему регистру.
Пример: `ACDUU-490` создаст каталог `acduu-490`.

```text
.gitflame-ci.yml
.gitignore
.python-version
README.md
pyproject.toml
uv.lock
modules/__init__.py
modules/main.py
tests/test_main.py
```

Папка `modules` предназначена для рабочего кода. В неё можно добавлять свои
пакеты, манифесты и дополнительные модули.

## Требования

Нужен Python `3.13`. Файл `.python-version` в проекте фиксирует `3.13.3`.
Также нужны `pip`, `git`, Cookiecutter и `uv`.

## Проверка Python

Windows:

```powershell
py -3.13 --version
```

macOS и Linux:

```bash
python3.13 --version
```

Ожидается Python версии `3.13.x`. Если Python не установлен, скачайте его с
официального сайта Python. На Windows включите добавление Python в `PATH`.
На macOS можно использовать официальный установщик Python, на Linux — пакетный
менеджер вашего дистрибутива.

## Проверка pip

Windows:

```powershell
py -3.13 -m pip --version
py -3.13 -m ensurepip --upgrade
```

macOS и Linux:

```bash
python3.13 -m pip --version
python3.13 -m ensurepip --upgrade
```

Общая форма проверки: `python -m pip --version`.
Общая форма восстановления: `python -m ensurepip --upgrade`.
Если `ensurepip` недоступен, установите Python заново из официального источника.

## Проверка git

```bash
git --version
```

На Windows установите Git for Windows. На macOS Git обычно ставится вместе с
Command Line Tools. На Linux установите Git через пакетный менеджер.

## Проверка Cookiecutter

```bash
python -m cookiecutter --version
python -m pip install cookiecutter
```

Для Python 3.13 на macOS и Linux:

```bash
python3.13 -m pip install cookiecutter
```

Для Windows:

```powershell
py -3.13 -m pip install cookiecutter
```

## Проверка uv

```bash
uv --version
python -m pip install uv
uv --version
```

## Что передаётся после cookiecutter

Аргумент после `cookiecutter` — это GitHub URL или путь к локальной копии
шаблона. GitHub URL указывает на публичный репозиторий с этим шаблоном.
Локальный путь указывает на каталог, где лежит `cookiecutter.json`.

```bash
python -m cookiecutter https://github.com/AntonNovozhilov/project-template
python -m cookiecutter ./project_template_main
```

## Вопросы Cookiecutter

`Введите номер заявки, например ACDUU-490` — номер заявки.
Разрешены латинские буквы, цифры, `-` и `_`.
`-` и `_` не должны быть первым или последним символом.
`-` и `_` не должны повторяться подряд.

`Введите понятное название автоматизации` — человекочитаемое название проекта.
`Введите e-mail автора` — e-mail автора; проверяется общий формат e-mail.
`Введите отделы через запятую или оставьте пустым` — список отделов.
Пример: `Отдел 1, Группа 2`.
Пустое значение разрешено и будет записано как `[]`.
Непустой список будет записан как JSON-массив.
`Введите краткое описание автоматизации` — отдельное описание до 255 символов.

## Где создаётся проект

Cookiecutter создаёт проект в текущем каталоге запуска. Если команда запущена
из `~/projects`, результат появится в `~/projects/acduu-490`.
Каталог результата не является Git-репозиторием. Это сделано специально:
после переноса в корпоративный контур можно выполнить `git init`, добавить
корпоративный GitLab remote и запушить проект.

## Работа с uv

`uv sync` создаёт окружение и ставит зависимости из `pyproject.toml` и `uv.lock`.
`uv add` добавляет runtime-зависимость.
`uv remove` удаляет зависимость.
`uv lock` пересобирает файл блокировки.
`uv run` запускает команду внутри окружения.

```bash
uv sync
uv add pandas
uv remove pandas
uv lock
uv run python -m modules.main
uv run pytest
```

## Про Феникс

Вне корпоративного контура используется обычный публичный PyPI. Шаблон не
переключает индекс пакетов на Феникс. В корпоративном контуре установка
библиотек через Феникс должна обеспечиваться средой.

## Проверка результата

После генерации перейдите в каталог проекта, проверьте структуру файлов,
запустите `uv sync`, затем `uv run pytest`. Если тесты прошли, минимальная
структура проекта готова к разработке.
