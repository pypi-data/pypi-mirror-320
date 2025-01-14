from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from dj_settings import ConfigParser

from pvenv.subcommands.base import BaseCommand

if TYPE_CHECKING:
    from argparse import Namespace


class Command(BaseCommand):
    __slots__ = ("cd", "venv")

    def __init__(self, options: Namespace) -> None:
        super().__init__(options)
        self.venv: str = options.venv
        self.cd: bool = options.cd

    def run(self) -> None:
        venv_path = self.base_dir.joinpath(self.venv)
        if not venv_path.exists():
            msg = f"Venv {self.venv} doesn't exist, aborting..."
            raise RuntimeError(msg)

        if os.getenv("VIRTUAL_ENV"):
            self.execute("dvenv")

        project = venv_path.joinpath(".project")
        if project.exists():
            if self.cd:
                with project.open() as file:
                    self.execute(f"cd {file.read().strip()}")
            environment = venv_path.joinpath(".environment")
            if environment.exists():
                new_environment: dict[str, Any] = {}  # type: ignore[misc]
                with environment.open() as file:
                    for line in file:
                        new_environment |= ConfigParser([line.strip()]).data
                environment_string = " ".join(
                    f"{key}={value}" for key, value in new_environment.items()
                )
                self.execute(f"invenv {environment_string}")

        activate = venv_path.joinpath("bin/activate")
        if activate.exists():
            self.execute(f". {activate}")
            self.execute(f"invenv UV_PROJECT_ENVIRONMENT={venv_path}")
        else:
            self.execute(f"export VIRTUAL_ENV=dummy_{self.venv}")
