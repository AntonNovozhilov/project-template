# Шаблон Python-скрипта для ScriptHub

Этот репозиторий содержит публичный Cookiecutter-шаблон для создания проекта
вне корпоративного контура. Сгенерированный проект можно разрабатывать локально,
а потом перенести внутрь компании и создать там обычный GitLab-репозиторий.

Шаблон не создаёт удалённый репозиторий, не делает `git push`, не создаёт `.git`
в результате и не устанавливает зависимости автоматически. Установка выполняется
отдельно командой `uv sync`.

## Что будет создано

Имя каталога берётся из `CI_CD_DISPLAY_NAME` и приводится к нижнему регистру.
Пример: `RPA-490` создаст каталог `rpa-490`.

```text
.gitflame-ci.yml
.gitignore
.python-version
README.md
pyproject.toml
Makefile
modules/__init__.py
modules/main.py
tests/test_main.py
```

Папка `modules` предназначена для рабочего кода. В неё можно добавлять свои
пакеты, манифесты и дополнительные модули. Runtime-данные каждого проекта
хранятся отдельно в `~/.rpa/<project-name>/`: конфигурация, состояние и ресурсы
не смешиваются между проектами.
При повторном запуске уже существующие файлы в `assets` не перезаписываются,
поэтому локальные изменения mapping-файлов сохраняются.

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
python3 -m cookiecutter https://github.com/AntonNovozhilov/project-template
python3 -m cookiecutter ./project_template_main
```

## Вопросы Cookiecutter

`Введите номер заявки, например RPA-490` — номер заявки.
Разрешены латинские буквы, цифры, `-` и `_`.
`-` и `_` не должны быть первым или последним символом.
`-` и `_` не должны повторяться подряд.

`Введите понятное название автоматизации` — человекочитаемое название проекта.
`Введите e-mail автора в доменной зоне rt.ru` — e-mail автора; адрес должен
быть в домене `rt.ru`.
`Введите отделы через запятую или оставьте пустым` — список отделов.
Пример: `Отдел 1, Группа 2`.
Пустое значение разрешено и будет записано как `[]`.
Непустой список будет записан как JSON-массив.
`Введите краткое описание автоматизации` — отдельное описание до 255 символов.

## Где создаётся проект

Cookiecutter создаёт проект в текущем каталоге запуска. Если команда запущена
из `~/projects`, результат появится в `~/projects/rpa-490`.
Каталог результата не является Git-репозиторием. Это сделано специально:
после переноса в корпоративный контур можно выполнить `git init`, добавить
корпоративный GitLab remote и запушить проект.

## Работа с uv

`uv sync` создаёт окружение и ставит зависимости из `pyproject.toml` и созданного
в контуре `uv.lock`.
`uv add` добавляет runtime-зависимость.
`uv remove` удаляет зависимость.
`uv lock` создаёт или пересобирает файл блокировки.
`uv run` запускает команду внутри окружения.

```bash
uv sync
uv add pandas
uv remove pandas
uv lock
uv run python -m modules.main
uv run pytest
```

## Установка через Phoenix

В сгенерированном проекте Makefile настроен на корпоративный индекс Феникс.
Из каталога проекта выполните:

```bash
python3.13 -m pip install --upgrade \
    --index-url "https://repository.rt.ru/repository/pypi-pypi.org/simple-allowed" \
    uv
make
```

Команда задаёт `UV_DEFAULT_INDEX`, выбирает Python 3.13, пересобирает `uv.lock`
через Феникс и выполняет `uv sync --locked`.

Если Makefile использовать нельзя, выполните те же действия вручную:

```bash
export UV_DEFAULT_INDEX="https://repository.rt.ru/repository/pypi-pypi.org/simple-allowed"
export UV_PYTHON="3.13"
uv lock --python 3.13
uv sync --locked --python 3.13
```

Если проект был создан старой версией шаблона и `uv lock` сообщает об ошибке
разбора `uv.lock`, сохраните старый файл и пересоберите его:

```bash
mv uv.lock uv.lock.broken
export UV_DEFAULT_INDEX="https://repository.rt.ru/repository/pypi-pypi.org/simple-allowed"
export UV_PYTHON="3.13"
uv lock --python 3.13
uv sync --locked --python 3.13
```

В локальной разработке без Makefile команды `uv lock` и `uv sync` используют
публичный PyPI.

## Про Феникс

Вне корпоративного контура используется обычный публичный PyPI. В корпоративном
контуре используйте `make` или ручную настройку `UV_DEFAULT_INDEX`, приведённую
выше. Логин и пароль не записывайте в Makefile, `pyproject.toml` или `uv.lock`.

## Проверка результата

После генерации перейдите в каталог проекта, проверьте структуру файлов,
запустите `uv sync`, затем `uv run pytest`. Если тесты прошли, минимальная
структура проекта готова к разработке.
