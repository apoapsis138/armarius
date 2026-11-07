"""The desktop covenant's Charter chapter: its Charter of Covenant (the
name, when it was sworn, the members' seals, the preamble) and its
clauses ruled off on the page under their charter sections, with Edit
Charter, Seal the Charter, Add, Edit, Delete and Break a Clause; the
chosen clause shows in the inspector. What it says comes from the core
(covenant_charter.py, forms/charter.py), as the terminal's Charter tab
does.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from .. import artwork, section_verbs
from .. import covenant_charter as cc
from ..forms import charter as charter_forms
from ..markup import escape
from ..models import (
    CLAUSE_BROKEN,
    STANDING_ASSOCIATE,
    STANDING_EXPELLED,
    STANDING_FULL,
    STANDING_GUEST,
    STANDING_PROBATION,
    CharterClause,
    Covenant,
    Saga,
)
from ..sections import CHARTER_SECTION, CLAUSES_SECTION
from . import pictures
from .character_sheet import TextBlock, section
from .editing import Chooser, RowVerb, Run, verb_buttons
from .figures import fact_grid, prose
from .medallions import empty_seal, member_seal
from .ruled_entry import RuledEntry
from .themes import Palette
from .widgets import badge, edit_button, serif, text

#: Inspect: the inspector's title, the line under it, and its markup.
Inspect = Callable[[str, str, str], None]


class SealCell(QWidget):
    """One magus's seal on the charter, his name and when he sealed it
    beneath; a dashed ring for one who hasn't sworn yet."""

    RADIUS = 21

    def __init__(self, shown: cc.SealShown, p: Palette) -> None:
        super().__init__()
        self.shown, self.p = shown, p
        self.setFixedSize(108, 2 * self.RADIUS + 52)
        name = shown.character.name
        standing = cc.standing_words(shown.seal) if shown.seal else ""
        self.setToolTip(
            f"{name}: sealed {shown.when}" + (f", {standing}" if standing else "")
            if shown.seal
            else f"{name}: not yet sworn"
        )

    def _under(self) -> str:
        return _seal_under(self.shown)

    def paintEvent(self, _event: QPaintEvent) -> None:
        g = QPainter(self)
        g.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.RADIUS
        c = QPointF(self.width() / 2, r + 6)
        character = self.shown.character
        if self.shown.seal is not None:
            symbol = artwork.person_symbol(character)
            mark = (
                pictures.pixmap(symbol, self.p["foreground"], round(r * 1.05), 2.0)
                if symbol is not None
                else None
            )
            member_seal(g, c, r, mark, character.name[:1].upper())
            if self.shown.expelled:
                # An expelled magus's seal stays on the charter, struck.
                pen = QPen(QColor(self.p["text-error"]), 2.5)
                g.setPen(pen)
                g.drawLine(
                    QPointF(c.x() - r * 1.1, c.y() + r * 0.9),
                    QPointF(c.x() + r * 1.1, c.y() - r * 0.9),
                )
        else:
            empty_seal(g, c, r, self.p)
        name = character.name.split(" of ")[0]
        f = QFont(pictures.SERIF)
        f.setPointSizeF(10.5)
        g.setFont(f)
        g.setPen(self.p["foreground"] if self.shown.seal else self.p["dim"])
        top = 2 * r + 12
        g.drawText(
            QRectF(0, top, self.width(), 18),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            name,
        )
        f.setItalic(True)
        f.setPointSizeF(9.5)
        g.setFont(f)
        g.setPen(self.p["label"] if self.shown.seal else self.p["dim"])
        g.drawText(
            QRectF(0, top + 17, self.width(), 18),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            self._under(),
        )
        g.end()


#: A standing as the line under a seal says it.
SHORT_STANDINGS = {
    STANDING_ASSOCIATE: "associate",
    STANDING_PROBATION: "probationary",
    STANDING_GUEST: "guest",
    STANDING_EXPELLED: "expelled",
}


def _seal_under(shown: cc.SealShown) -> str:
    """The line under a seal: when it was sealed, or the standing that
    matters more (probationary, expelled, associate, guest)."""
    if shown.seal is None:
        return "not yet sworn"
    if shown.seal.standing != STANDING_FULL:
        # One word: the seal's cell is narrow.
        return SHORT_STANDINGS.get(shown.seal.standing, shown.seal.standing)
    return shown.when if shown.when != "—" else "sealed"


def seal_row(saga: Saga, covenant: Covenant, p: Palette) -> QWidget:
    """The members' seals in a row, those still to swear last."""
    box = QWidget()
    row = QHBoxLayout(box)
    row.setContentsMargins(0, 2, 0, 0)
    row.setSpacing(4)
    shown = cc.seals(saga, covenant)
    if not shown:
        row.addWidget(text("No magi yet to seal it.", p["dim"], serif(12, italic=True)))
    for found in shown:
        row.addWidget(SealCell(found, p))
    row.addStretch(1)
    return box


def _quiet(block: TextBlock) -> TextBlock:
    """A text block that lets clicks through to the entry it sits in."""
    block.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
    block.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    return block


class ClauseEntry(RuledEntry):
    """One clause ruled off on the page: its number as a rubric in the
    margin (a § for one with a title), when it was agreed and its status,
    its words (struck through and dimmed when broken), and how it was
    broken or amended."""

    def __init__(self, saga: Saga, clause: CharterClause, p: Palette) -> None:
        super().__init__(p)
        row = self.ruled_row()
        broken = clause.status == CLAUSE_BROKEN
        numbered = cc.is_numbered(clause)
        number = text(
            cc.clause_mark(clause) if numbered else "§",
            p["dim"] if broken else p["heading"],
            serif(20, bold=True),
        )
        number.setFixedWidth(40)
        number.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        row.addWidget(number, 0, Qt.AlignmentFlag.AlignTop)
        column = QVBoxLayout()
        column.setSpacing(3)
        top = QHBoxLayout()
        top.setSpacing(8)
        if not numbered:
            top.addWidget(
                text(
                    clause.number.strip() or "—",
                    p["heading"],
                    serif(12.5, bold=True, caps=True),
                )
            )
        top.addWidget(
            text(
                f"Agreed {cc.when(clause.year, clause.season)}",
                p["label"],
                serif(11, italic=True),
            )
        )
        top.addStretch(1)
        tone = p[cc.STATUS_COLOURS.get(clause.status, "text-success")]
        top.addWidget(badge(cc.status_words(clause), tone, p))
        column.addLayout(top)
        words = _quiet(TextBlock(cc.clause_text(clause), p))
        words.setFont(serif(13.5))
        column.addWidget(words)
        for extra in (cc.note_line(clause), cc.censure_line(saga, clause)):
            if extra:
                note = _quiet(TextBlock(extra, p))
                note.setFont(serif(12))
                column.addWidget(note)
        row.addLayout(column, 1)


def _choose_entries(
    entries: Sequence[ClauseEntry], indexes: Sequence[int], chooser: Chooser
) -> None:
    """Clicking entry i chooses clause `indexes[i]`; the chosen one is
    bracketed."""
    for entry, index in zip(entries, indexes, strict=True):
        before = entry.clicked

        def clicked(index: int = index, before: Callable[[], None] = before) -> None:
            chooser.choose(index)
            before()

        entry.clicked = clicked

    def mark(chosen: int | None) -> None:
        for entry, index in zip(entries, indexes, strict=True):
            entry.set_chosen(index == chosen)

    chooser.listeners.append(mark)


def charter_buttons(saga: Saga, covenant: Covenant, p: Palette, run: Run) -> list:
    """The charter's own buttons: Seal the Charter and the templates'
    Use and Save always; Forget a Template while the saga keeps one, and
    End Membership while an expelled magus is still of the covenant."""
    found = [
        edit_button(
            "Seal the Charter",
            p,
            lambda: run(charter_forms.seal_form(saga, covenant)),
            "charter",
        ),
        edit_button(
            charter_forms.USE_TEMPLATE,
            p,
            lambda: run(charter_forms.use_template(saga, covenant)),
            "worksheet",
        ),
        edit_button(
            charter_forms.SAVE_TEMPLATE,
            p,
            lambda: run(charter_forms.save_template(saga, covenant)),
            "export",
        ),
    ]
    if saga.charter_templates:
        found.append(
            edit_button(
                charter_forms.FORGET_TEMPLATE,
                p,
                lambda: run(charter_forms.forget_template(saga)),
                "delete",
            )
        )
    if charter_forms.can_end_membership(saga, covenant):
        found.append(
            edit_button(
                charter_forms.END_MEMBERSHIP,
                p,
                lambda: run(charter_forms.end_membership_step(saga, covenant)),
                "close",
            )
        )
    return found


def law_note(saga: Saga, covenant: Covenant, p: Palette) -> TextBlock:
    """What the law makes of the charter, the Tribunal's customs, and
    what waits on the troupe (an expelled magus still of the covenant, a
    probation run its term)."""
    lines = [f"[dim]{escape(cc.law_line(saga, covenant))}[/]"]
    if note := cc.custom_note(saga, covenant):
        lines.append(f"[dim]{escape(note)}[/]")
    for line in cc.probations_ended(saga, covenant):
        lines.append(
            f"[$text-warning]{escape(line)}: Seal the Charter to make him a full "
            "member, or extend it.[/]"
        )
    if out := cc.still_resident(saga, covenant):
        names = ", ".join(escape(c.name) for c in out)
        lines.append(
            f"[$text-warning]Expelled but still of the covenant: {names}. "
            "End Membership removes them.[/]"
        )
    block = TextBlock("\n".join(lines), p)
    block.setFont(serif(12))
    return block


def charter_section(saga: Saga, covenant: Covenant, p: Palette, run: Run) -> QWidget:
    """The charter: its name, its facts, the members' seals, its preamble
    and what the law makes of it, with Edit Charter, Seal the Charter and
    the templates."""
    charter = cc.charter_of(covenant)
    widget = section(
        cc.charter_title(charter),
        p,
        fact_grid(cc.facts(saga, covenant), p, 4),
        seal_row(saga, covenant, p),
        prose(charter.preamble.strip(), p)
        if charter.preamble.strip()
        else text(
            "No preamble yet: Edit Charter to write its oath.",
            p["dim"],
            serif(12.5, italic=True),
        ),
        law_note(saga, covenant, p),
        edits={"Edit Charter": lambda: run(charter_forms.charter_form(saga, covenant))},
        buttons=charter_buttons(saga, covenant, p, run),
    )
    widget.setObjectName(CHARTER_SECTION)
    return widget


def clauses_section(
    saga: Saga, covenant: Covenant, p: Palette, run: Run, inspect: Inspect
) -> QWidget:
    """The clauses under their charter sections, with Add, Edit, Delete
    and Break a Clause on the chosen one."""
    charter = cc.charter_of(covenant)
    chooser = Chooser()
    body = QWidget()
    stack = QVBoxLayout(body)
    stack.setContentsMargins(0, 0, 0, 0)
    stack.setSpacing(2)
    entries: list[ClauseEntry] = []
    indexes: list[int] = []
    for name, found in cc.grouped(charter):
        if name:
            heading = text(name, p["heading"], serif(11.5, bold=True, caps=True))
            heading.setContentsMargins(12, 8, 0, 0)
            stack.addWidget(heading)
        for index in found:
            entry = ClauseEntry(saga, charter.clauses[index], p)

            def show(index: int = index) -> None:
                title, subtitle = cc.inspector_title(charter, index)
                inspect(title, subtitle, cc.info(saga, covenant, index, wide=False))

            entry.clicked = show
            entries.append(entry)
            indexes.append(index)
            stack.addWidget(entry)
    _choose_entries(entries, indexes, chooser)
    if not charter.clauses:
        stack.addWidget(
            text("No clauses yet: Add the first.", p["dim"], serif(12.5, italic=True))
        )
    more: list[RowVerb] = [
        (
            "Break a Clause",
            "threat",
            lambda row: charter_forms.break_clause(saga, covenant, row),
            lambda row: charter_forms.can_break(covenant, row),
        ),
        (
            charter_forms.CENSURE,
            "threat",
            lambda row: charter_forms.censure_clause(saga, covenant, row),
            lambda row: charter_forms.can_censure(covenant, row),
        ),
        (
            charter_forms.CHARGE,
            "tribunal",
            lambda row: charter_forms.charge(saga, covenant, row),
            lambda row: charter_forms.can_charge(saga, covenant, row),
        ),
    ]
    widget = section(
        cc.clauses_title(charter),
        p,
        body,
        buttons=verb_buttons(
            section_verbs.ops_of(saga, covenant)[CLAUSES_SECTION],
            chooser,
            run,
            p,
            more=more,
        ),
    )
    widget.setObjectName(CLAUSES_SECTION)
    return widget
