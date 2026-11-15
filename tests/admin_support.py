"""Running the admin word in a test: a terminal whose answers are given
beforehand, and helpers that say whether a verb did its work."""

from __future__ import annotations

from collections.abc import Iterator

from ars_magica_manager import admin


class FakeConsole(admin.Console):
    """A terminal whose answers are given beforehand and whose output is kept."""

    def __init__(
        self, answers: list[str] | None = None, secrets: list[str] | None = None
    ):
        self.printed: list[str] = []
        self.errors: list[str] = []
        self.asked: list[str] = []
        self.code: int | None = None
        answered: Iterator[str] = iter(answers or [])
        hidden: Iterator[str] = iter(secrets or [])

        def ask(prompt: str) -> str:
            self.asked.append(prompt)
            try:
                return next(answered)
            except StopIteration:
                raise EOFError from None

        def secret(prompt: str) -> str:
            self.asked.append(prompt)
            return next(hidden)

        super().__init__(self.printed.append, self.errors.append, ask, secret)

    @property
    def text(self) -> str:
        return "\n".join(self.printed)


def run(argv: list[str], console: FakeConsole | None = None) -> FakeConsole:
    console = console or FakeConsole()
    console.code = admin.run(argv, console)
    return console


def ok(argv: list[str], console: FakeConsole | None = None) -> FakeConsole:
    """Run a verb that should do its work; its console."""
    done = run(argv, console)
    assert done.code == 0, done.errors
    return done


def refused(argv: list[str], console: FakeConsole | None = None) -> str:
    """Run a verb that should refuse; why it did."""
    done = run(argv, console)
    assert done.code == 1, done.printed
    return "\n".join(done.errors)
