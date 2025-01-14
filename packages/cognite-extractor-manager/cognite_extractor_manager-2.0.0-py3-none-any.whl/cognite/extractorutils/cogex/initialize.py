#  Copyright 2021 Cognite AS
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
from typing import Dict

import requests
from humps import pascalize

from cognite.extractorutils.cogex.io import choice, get_git_user, prompt

pyproject_template = """[project]
name = "{name}"
version = "1.0.0"
description = "{description}"
authors = [ {{ name = "{author_name}", email = "{author_email}" }} ]
requires-python = ">=3.11"
readme = "README.md"

dependencies = [
]

[dependency-groups]
dev = [
    "pyinstaller>=6.0",
    "macholib>=1.16.3 ; sys_platform == 'darwin'",      # Used by pyinstaller on Mac OS
    "pefile>=2023.2.7 ; sys_platform == 'win32'",       # Used by pyinstaller on Windows
    "pywin32-ctypes>=0.2.3 ; sys_platform == 'win32'",  # Used by pyinstaller on Windows
]

[project.scripts]
{name} = "{name}.__main__:main"

[tool.ruff]
target-version = "py311"
exclude = [".git", ".mypy_cache", ".ruff_cache"]
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "T20", "UP"]
ignore = []
fixable = ["A", "B", "C", "D", "E", "F", "I", "UP"]
unfixable = []

# Allow unused variables when underscore-prefixed.
dummy-variable-rgx = "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"

[tool.mypy]
pretty = true
check_untyped_defs = true
ignore_missing_imports = false
disallow_untyped_defs = true
follow_imports = "normal"
namespace_packages = true
explicit_package_bases = true
show_error_codes = true
exclude = ["tests/*"]

[tool.hatch.build.targets.wheel]
packages = ["{name}"]

[tool.hatch.build.targets.sdist]
only-include = ["{name}"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""

pre_commit_template = """
repos:
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
    rev: v0.9.0
  - repo: local
    hooks:
      - id: mypy
        name: mypy
        entry: uv run mypy {name}
        language: system
        types: [python]
        pass_filenames: false
"""

basic_config_template = """
from dataclasses import dataclass, field

from cognite.extractorutils.configtools import BaseConfig, StateStoreConfig


@dataclass
class ExtractorConfig:
    state_store: StateStoreConfig = field(default_factory=StateStoreConfig)


@dataclass
class Config(BaseConfig):
    extractor: ExtractorConfig = field(default_factory=ExtractorConfig)
"""

basic_configfile_template = """
logger:
    console:
        level: INFO

cognite:
    # Read these from environment variables
    host: ${{COGNITE_BASE_URL}}
    project: ${{COGNITE_PROJECT}}

    idp-authentication:
        token-url: ${{COGNITE_TOKEN_URL}}

        client-id: ${{COGNITE_CLIENT_ID}}
        secret: ${{COGNITE_CLIENT_SECRET}}
        scopes:
            - ${{COGNITE_BASE_URL}}/.default
"""

basic_main_template = """
from cognite.extractorutils import Extractor

from {name} import __version__
from {name}.extractor import run_extractor
from {name}.config import Config


def main() -> None:
    with Extractor(
        name="{name}",
        description="{description}",
        config_class=Config,
        run_handle=run_extractor,
        version=__version__,
    ) as extractor:
        extractor.run()


if __name__ == "__main__":
    main()
"""

basic_extractor_template = """
import logging
from threading import Event

from cognite.client import CogniteClient
from cognite.extractorutils.statestore import AbstractStateStore

from {name}.config import Config


def run_extractor(cognite: CogniteClient, states: AbstractStateStore, config: Config, stop_event: Event) -> None:
    logging.info("Hello, world!")
"""

basic_template: Dict[str, str] = {
    "example_config.yaml": basic_configfile_template,
    os.path.join("{name}", "config.py"): basic_config_template,
    os.path.join("{name}", "extractor.py"): basic_extractor_template,
    os.path.join("{name}", "__main__.py"): basic_main_template,
}

class_extractor_template = """
from cognite.extractorutils import Extractor

from {name} import __version__
from {name}.config import Config


class {class_name}(Extractor[Config]):
    def __init__(self) -> None:
        super().__init__(
            name="{name}",
            description="{description}",
            config_class=Config,
            version=__version__,
        )

    def run(self) -> None:
        self.logger.info("Hello, world!")
"""

class_main_template = """
from {name}.extractor import {class_name}


def main() -> None:
    with {class_name}() as extractor:
        extractor.run()


if __name__ == "__main__":
    main()
"""

class_template: Dict[str, str] = {
    "example_config.yaml": basic_configfile_template,
    os.path.join("{name}", "config.py"): basic_config_template,
    os.path.join("{name}", "extractor.py"): class_extractor_template,
    os.path.join("{name}", "__main__.py"): class_main_template,
}


rest_configfile_template = """
logger:
    console:
        level: INFO

cognite:
    # Read these from environment variables
    host: ${{COGNITE_BASE_URL}}
    project: ${{COGNITE_PROJECT}}

    idp-authentication:
        token-url: ${{COGNITE_TOKEN_URL}}

        client-id: ${{COGNITE_CLIENT_ID}}
        secret: ${{COGNITE_CLIENT_SECRET}}
        scopes:
            - ${{COGNITE_BASE_URL}}/.default

source:
    auth:
        basic:
            username: my-user
            password: ${{SOURCE_PASSWORD}}
"""

rest_main_template = """
from {name} import __version__
from {name}.extractor import extractor


def main() -> None:
    with extractor:
        extractor.run()


if __name__ == "__main__":
    main()
"""

rest_extractor_template = """
import arrow

from cognite.extractorutils.uploader_types import Event
from cognite.extractorutils.rest.extractor import RestExtractor

from {name} import __version__
from {name}.dto import ElementList

extractor = RestExtractor(
    name="{name}",
    description="{description}",
    version=__version__,
)

@extractor.get("/elements", response_type=ElementList, interval=60)
def elements_to_events(element_list: ElementList) -> Iterable[Event]:
    for element in element_list.elements:
        start_time = arrow.get(element.startTime)
        end_time = start_time.shift(minutes=element.duration)

        yield Event(start_time=start_time, end_time=end_time, description=element.description)
"""

rest_dto_template = """
from dataclasses import dataclass
from typing import List

@dataclass
class MyElement:
    elementId: str
    eventTime: str
    duration: int
    description: str

@dataclass
class ElementList:
    elements: List[MyElement]
"""

rest_template: Dict[str, str] = {
    "example_config.yaml": rest_configfile_template,
    os.path.join("{name}", "extractor.py"): rest_extractor_template,
    os.path.join("{name}", "dto.py"): rest_dto_template,
    os.path.join("{name}", "__main__.py"): rest_main_template,
}


templates: Dict[str, Dict[str, str]] = {"simple": basic_template, "rest": rest_template, "class": class_template}


def initialize_project() -> None:
    name = prompt("extractor name").replace(" ", "_").replace("-", "_").lower()
    description = prompt("description")
    git_name, git_email = get_git_user()
    author_name = prompt("author name", git_name)
    author_email = prompt("author email", git_email)

    print("Which template should be loaded?")
    print(
        "  simple: loads a generic template suitable for most source systems, using\n"
        "          a simple function as the main entrypoint for the extractor.\n"
        "          Most suitable for small and simple extractors.\n"
    )
    print(
        "  class:  loads a generic template suitable for most source systems, using\n"
        "          a run method on a class as the main entrypoint for the extractor.\n"
        "          Most suitable for slightly bigger and more complicated extractors.\n"
    )
    print(
        "  rest:   loads a template for extracting from RESTful APIs, using the REST\n"
        "          extension for extractor-utils\n"
    )
    template = choice("template", ["simple", "class", "rest"], "simple")

    with open("pyproject.toml", "w") as pyproject_file:
        pyproject_file.write(
            pyproject_template.format(
                name=name,
                description=description,
                author_name=author_name,
                author_email=author_email,
            )
        )
    open("README.md", "w").close()
    with open(".pre-commit-config.yaml", "w") as pre_commit_file:
        pre_commit_file.write(pre_commit_template.format(name=name))
    print("Fetching gitignore template from GitHub")
    gitignore_template = requests.get("https://raw.githubusercontent.com/github/gitignore/master/Python.gitignore").text
    with open(".gitignore", "w") as gitignore_file:
        gitignore_file.write(gitignore_template)

    if not os.path.isdir(".git"):
        os.system("git init")

    os.mkdir(name)
    with open(os.path.join(name, "__init__.py"), "w") as init_file:
        init_file.write('__version__ = "1.0.0"')
    for path, content in templates[template].items():
        with open(path.format(name=name), "w") as f:
            f.write(content.format(name=name, description=description, class_name=pascalize(name)))

    os.system("uv add cognite-extractor-utils")
    if template == "rest":
        os.system("uv add cognite-extractor-utils-rest")
    os.system("uv add --dev mypy ruff pre-commit")
    os.system("uv sync")
    os.system("uv run pre-commit autoupdate")
    os.system("uv run pre-commit install")
    os.system(f"uv run ruff check --fix {name}")
    os.system(f"uv run ruff format {name}")
