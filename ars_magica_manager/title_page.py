"""The title page the app opens on: its name and tagline, the version and
the name of its major version, and the ways on (the saga opened last, every
saga, a new saga, and Help). Both front-ends lay out the same TitlePage.

The saga opened last is remembered in the settings, so Open Saga (and
Enter) can go straight back to it.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import ROOT, __version__, changelog, settings, storage

NAME = "Armarius"
TAGLINE = "A saga manager for Ars Magica"

#: The settings key holding the id of the saga opened last.
LAST_SAGA = "last_saga"

#: The ways on, by key.
OPEN, SAGAS, NEW, HELP = "open", "sagas", "new", "help"


@dataclass(frozen=True)
class TitleChoice:
    key: str
    label: str
    detail: str


@dataclass(frozen=True)
class TitlePage:
    name: str
    tagline: str
    #: "Version 2.104.0 · Codex · for Ars Magica Fifth Edition".
    edition: str
    choices: tuple[TitleChoice, ...]
    #: The saga Open Saga opens; None when there is none to open.
    saga_id: str | None


def release_name(text: str | None = None) -> str:
    """This version's major version's name, from CHANGELOG.md ("" if it
    has none, or the file can't be read)."""
    if text is None:
        try:
            text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        except OSError:
            return ""
    return changelog.release_name(text, __version__)


def remember_saga(saga_id: str) -> None:
    """Note `saga_id` as the saga opened last."""
    settings.update_settings(**{LAST_SAGA: saga_id})


def last_saga(saga_ids: list[str]) -> str | None:
    """The saga Open Saga opens, of `saga_ids` (the sagas saved): the one
    opened last, else the only one there is."""
    remembered = settings.load_settings().get(LAST_SAGA)
    if isinstance(remembered, str) and remembered in saga_ids:
        return remembered
    return saga_ids[0] if len(saga_ids) == 1 else None


def _saga_name(saga_id: str) -> str | None:
    try:
        return storage.load_saga(saga_id).name
    except OSError, ValueError, TypeError, KeyError:
        return None


def title_page(saga_ids: list[str] | None = None) -> TitlePage:
    """The title page for the sagas `saga_ids` (all saved ones by
    default). Only the storyguide's own window opens on it: a player's
    copy of a hosted saga goes straight to the sagas, to sign in."""
    saga_ids = storage.list_sagas() if saga_ids is None else saga_ids
    release = release_name()
    edition = " · ".join(
        part
        for part in (f"Version {__version__}", release, "for Ars Magica Fifth Edition")
        if part
    )
    saga_id = last_saga(saga_ids)
    name = _saga_name(saga_id) if saga_id else None
    if name is None:
        saga_id = None
    choices = []
    if saga_id is not None:
        choices.append(TitleChoice(OPEN, "Open Saga", name or ""))
    choices.append(
        TitleChoice(
            SAGAS,
            "All Sagas",
            "Choose one to open" if saga_ids else "None saved yet",
        )
    )
    choices.append(TitleChoice(NEW, "New Saga", "Begin a saga of your own"))
    choices.append(TitleChoice(HELP, "Help", "The guides and rules"))
    return TitlePage(NAME, TAGLINE, edition, tuple(choices), saga_id)
