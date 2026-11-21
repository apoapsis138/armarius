"""The desktop's Scenes lists (scenes.py): the saga's Scenes library in
Saga Management, with Add, Edit and Delete and the chosen Scene in the
inspector; and a Session page's Scenes, loaded in order, with Load, Edit
and Take Out (the core's SectionOps, as the terminal draws them)."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QVBoxLayout, QWidget

from .. import scenes, section_verbs
from ..forms import scenes as scene_forms
from ..models import Saga, Session
from ..sections import SCENES_SECTION, SESSION_SCENES_SECTION
from .character_sheet import section
from .editing import Chooser, Run, choose_rows, verb_buttons
from .sessions_section import sessions_section
from .themes import Palette
from .widgets import cells_table, serif, text

Inspect = Callable[[str, str, str], None]


def scenes_section(saga: Saga, p: Palette, run: Run, inspect: Inspect) -> QWidget:
    """The Scenes library; choosing a row shows the Scene in the inspector."""
    chooser = Chooser()
    rows = cells_table(
        scenes.SCENE_COLUMNS,
        [scenes.scene_cells(saga, s) for s in saga.scenes],
        p,
        lambda row: inspect(
            saga.scenes[row].title or "(untitled)",
            "Scene",
            scenes.scene_detail(saga, saga.scenes[row]),
        ),
    )
    choose_rows(rows, chooser)
    buttons = verb_buttons(
        section_verbs.ops_of(saga, saga)[SCENES_SECTION], chooser, run, p
    )
    return section(
        f"Scenes ({len(saga.scenes)})",
        p,
        rows
        if saga.scenes
        else text(
            "None yet: Add builds one to load into Sessions.",
            p["dim"],
            serif(12.5, italic=True),
        ),
        buttons=buttons,
        part=SCENES_SECTION,
    )


def sessions_and_scenes(saga: Saga, p: Palette, run: Run, inspect: Inspect) -> QWidget:
    """Saga Management's Sessions, then the Scenes library under them."""
    box = QWidget()
    column = QVBoxLayout(box)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(12)
    column.addWidget(sessions_section(saga, p, run, inspect))
    column.addWidget(scenes_section(saga, p, run, inspect))
    return box


def session_scenes_section(
    saga: Saga, session: Session, p: Palette, run: Run
) -> QWidget:
    """A Session's Scenes, in the evening's order."""
    chooser = Chooser()
    now = scene_forms.now_of(saga, session)
    rows = cells_table(
        scenes.USE_COLUMNS,
        [scenes.use_cells(saga, session, u, now) for u in session.scenes],
        p,
        lambda _row: None,
    )
    choose_rows(rows, chooser)
    buttons = verb_buttons(
        section_verbs.ops_of(saga, session)[SESSION_SCENES_SECTION],
        chooser,
        run,
        p,
        nouns=("Load a Scene", "Edit Scene", "Take Out"),
        part=SESSION_SCENES_SECTION,
    )
    return section(
        f"Scenes ({len(session.scenes)})",
        p,
        rows
        if session.scenes
        else text(
            "None yet: Load a Scene brings one from the library, or makes one.",
            p["dim"],
            serif(12.5, italic=True),
        ),
        buttons=buttons,
        part=SESSION_SCENES_SECTION,
    )
