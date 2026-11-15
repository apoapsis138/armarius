"""How the app starts another copy of itself, from a checkout or a Build.

Hosting runs the host as a process of its own, and the host runs a copy
of the terminal app for each player. From a checkout each is a Python
command (`python -m ...`, `python main.py`); a Build has no Python, so it
runs its own terminal program with a word saying what to run (`host`,
`seats`, `play`), which main.py looks up in its table of words. This
module is the one place that knows both layouts (a Facade): callers ask
for a word and get the command line to run.
"""

from __future__ import annotations

import sys
from pathlib import Path

from . import FROZEN, ROOT

#: The host for players: browsers, and SSH clients (tui/serve.py).
HOST = "host"
#: The listener for Remote seats (remote/serve.py).
SEATS = "seats"
#: One player's copy of the terminal app (main.py).
PLAY = "play"

#: What each word runs from a checkout: Python's arguments.
_FROM_SOURCE: dict[str, list[str]] = {
    HOST: ["-m", "ars_magica_manager.tui.serve"],
    SEATS: ["-m", "ars_magica_manager.remote.serve"],
    PLAY: [str(ROOT / "main.py")],
}
WORDS: frozenset[str] = frozenset(_FROM_SOURCE)

#: The Build's terminal program, beside its desktop one.
TERMINAL_PROGRAM = "armarius-terminal"


def python() -> str:
    """The Python to run a copy with: never pythonw, whose copies would
    have no console streams for the server to hand on."""
    executable = Path(sys.executable)
    if executable.stem.lower() == "pythonw":
        console = executable.with_name("python" + executable.suffix)
        if console.exists():
            return str(console)
    return str(executable)


def terminal_program() -> Path:
    """The Build's terminal program: beside whichever of its programs is
    running."""
    executable = Path(sys.executable)
    return executable.with_name(TERMINAL_PROGRAM + executable.suffix)


def command(word: str, *arguments: str) -> list[str]:
    """The command line that runs `word` with `arguments`."""
    if word not in WORDS:
        raise ValueError(f"No copy of the app runs {word!r}.")
    if FROZEN:
        return [str(terminal_program()), word, *arguments]
    return [python(), *_FROM_SOURCE[word], *arguments]


def command_line(word: str, *arguments: str) -> str:
    """`command` as one line, each part quoted, for a server that runs it
    through a shell (textual-serve, the SSH host)."""
    return " ".join(f'"{part}"' for part in command(word, *arguments))
