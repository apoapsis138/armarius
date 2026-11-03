"""Arms on the desktop: a record's Arms section (its shield, motto and
blazon, with Edit) and the row of its neighbours' arms. The shield itself
is painted by shields.py."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .. import arms as heraldry
from ..arms import Arms
from ..markup import escape
from ..models import Covenant, Neighbour, Saga
from .character_sheet import TextBlock, section
from .editing import Run
from .shields import pixmap
from .themes import Palette
from .widgets import serif, text


def shield_label(
    arms: Arms, width: int, edge: str, parent: QWidget | None = None
) -> QLabel:
    label = QLabel(parent)
    label.setPixmap(pixmap(arms, width, edge))
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label


#: The shield's width in an Arms section, and in a row of others' arms.
LARGE, SMALL = 110, 44


def arms_section(record: Covenant | Neighbour, p: Palette, run: Run) -> QWidget:
    """Arms: the shield, its motto and, smaller under it, its blazon,
    with Edit. The motto is the bearer's own words, so it leads."""
    found = heraldry.arms_of(record)
    body = QWidget()
    row = QHBoxLayout(body)
    row.setContentsMargins(0, 4, 0, 4)
    row.setSpacing(18)
    words = QVBoxLayout()
    words.setSpacing(6)
    if found is None:
        words.addWidget(text("No arms yet.", p["dim"], serif(12.5, italic=True)))
    else:
        row.addWidget(
            shield_label(found, LARGE, p["accent"]), 0, Qt.AlignmentFlag.AlignTop
        )
        if found.motto:
            words.addWidget(
                text(found.motto, p["foreground"], serif(17, italic=True), wrap=True)
            )
        words.addWidget(
            text(
                heraldry.blazon(found), p["label"], serif(12.5, italic=True), wrap=True
            )
        )
        said = heraldry.warning(found)
        if said:
            words.addWidget(TextBlock(f"[$text-warning]{escape(said)}[/]", p))
    words.addStretch(1)
    row.addLayout(words, 1)
    return section(
        "Arms", p, body, edits={"Edit Arms": lambda: run(heraldry.arms_form(record))}
    )


def neighbours_arms(saga: Saga, covenant: Covenant, p: Palette) -> QWidget | None:
    """The arms of the other covenants of the covenant's Tribunal, each
    with its name; None when none of them bears arms."""
    borne = [
        (c, found)
        for c in saga.covenants
        if c is not covenant
        and c.tribunal_id
        and c.tribunal_id == covenant.tribunal_id
        and (found := heraldry.arms_of(c)) is not None
    ]
    if not borne:
        return None
    body = QWidget()
    grid = QGridLayout(body)
    grid.setContentsMargins(0, 4, 0, 4)
    grid.setHorizontalSpacing(22)
    for column, (other, found) in enumerate(borne):
        cell = QWidget()
        stack = QVBoxLayout(cell)
        stack.setContentsMargins(0, 0, 0, 0)
        stack.setSpacing(4)
        shield = shield_label(found, SMALL, p["accent"])
        shield.setToolTip(heraldry.blazon(found))
        stack.addWidget(shield)
        name = text(other.name, p["label"], serif(11))
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stack.addWidget(name)
        grid.addWidget(cell, column // 8, column % 8)
    grid.setColumnStretch(min(len(borne), 8), 1)
    return section("Arms of the Tribunal's Covenants", p, body)
