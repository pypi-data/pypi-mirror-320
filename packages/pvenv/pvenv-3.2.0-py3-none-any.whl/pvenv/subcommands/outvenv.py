from __future__ import annotations

import os
from typing import TYPE_CHECKING

from pvenv.subcommands.base import BaseCommand

if TYPE_CHECKING:
    from argparse import Namespace


class Command(BaseCommand):
    __slots__ = ()

    def __init__(self, options: Namespace) -> None:
        super().__init__(options)

    def run(self) -> None:
        if self._prefix not in os.environ:
            return

        self.execute(f"unset {self._prefix}")
        prefix_size = len(self._prefix) + 1
        unset_prefix_size = len(self._prefix) + len("_UNSET") + 1
        for key, value in os.environ.items():
            if key.startswith(f"{self._prefix}_"):
                if key.startswith(f"{self._prefix}_UNSET_"):
                    self.execute(f"unset {key[unset_prefix_size:]}")
                else:
                    self.execute(f"export {key[prefix_size:]}={value}")
                self.execute(f"unset {key}")
