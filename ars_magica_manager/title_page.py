"""The title page the app opens on: its name and tagline, the version and
its release name, and the three ways on (the saga opened last, every
saga, and Help). Both front-ends lay out the same TitlePage.

The saga opened last is remembered in the settings, so Open Saga (and
Enter) can go straight back to it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from . import ROOT, __version__, settings, storage

NAME = "Armarius"
TAGLINE = "A saga manager for Ars Magica"

#: The settings key holding the id of the saga opened last.
LAST_SAGA = "last_saga"

#: A named release's heading in CHANGELOG.md: "## 2.52.0 — 2026-10-13 — Name".
_NAMED = re.compile(r"^## \d+\.\d+\.\d+ — [\d-]+ — (.+?)\s*$", re.MULTILINE)

#: The ways on, by key.
OPEN, SAGAS, HELP = "open", "sagas", "help"


@dataclass(frozen=True)
class TitleChoice:
    key: str
    label: str
    detail: str


@dataclass(frozen=True)
class TitlePage:
    name: str
    tagline: str
    #: "Version 2.52.0 · Nomen Novum · for Ars Magica Fifth Edition".
    edition: str
    choices: tuple[TitleChoice, ...]
    #: The saga Open Saga opens; None when there is none to open.
    saga_id: str | None


def release_name(changelog: str | None = None) -> str:
    """The name of the latest named release in CHANGELOG.md ("" if none
    is named, or the file can't be read)."""
    if changelog is None:
        try:
            changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        except OSError:
            return ""
    found = _NAMED.search(changelog)
    return found.group(1) if found else ""


def remember_saga(saga_id: str) -> None:
    """Note `saga_id` as the saga opened last."""
    settings.update_settings(**{LAST_SAGA: saga_id})


def last_saga(saga_ids: list[str]) -> str | None:
    """The saga Open Saga opens, of `saga_ids` (the sagas saved): the one
    opened last, else the only one there is."""
    remembered = settings.load_settings().get(LAST_SAGA)
    if remembered in saga_ids:
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
            "Choose or begin another" if saga_ids else "Begin your first saga",
        )
    )
    choices.append(TitleChoice(HELP, "Help", "The guides and rules"))
    return TitlePage(NAME, TAGLINE, edition, tuple(choices), saga_id)
