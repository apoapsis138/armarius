"""The desktop Tribunal page's Arguments chapter (Transforming Mythic
Europe pp. 27-35): the Tribunal's arguments, the chosen argument's reach,
Argument Total and debate bonus, and its texts, each a ledger of entries
ruled off on the page, with the chosen entry in the inspector, each
section's Add, Edit and Delete and the texts' Circulate a Text.

What it says and what its buttons do are forms/polemic.py's, as on the
terminal's Arguments tab."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..forms import charter_strength
from ..forms import polemic as pf
from ..models import Neighbour, Saga, Tribunal
from ..references import Fact
from .character_sheet import TextBlock, section
from .editing import Chooser, RowVerb, Run, verb_buttons
from .figures import fact_grid
from .ledger_rows import ledger_rows
from .themes import Palette
from .widgets import scrolling_page, serif, text

#: What a chosen entry shows in the inspector: its title, the line under
#: it and its details (markup).
Inspect = Callable[[str, str, str], None]


@dataclass
class ArgumentChoice:
    """The argument chosen on a Tribunal's chapter: kept while the saga is
    open, as the page is drawn again after every change."""

    argument: int | None = None


#: Each open Tribunal's choice, by the saga's and the Tribunal's ids.
_CHOICES: dict[tuple[str, str], ArgumentChoice] = {}


def choice_of(saga: Saga, tribunal: Tribunal) -> ArgumentChoice:
    return _CHOICES.setdefault((saga.id, tribunal.id), ArgumentChoice())


def _none(words: str, p: Palette) -> QWidget:
    return text(words, p["dim"], serif(12.5, italic=True), wrap=True)


class ArgumentsChapter(QWidget):
    """The chapter, drawn again in place when an argument is chosen (what
    the sections below show follows it)."""

    def __init__(
        self, saga: Saga, tribunal: Tribunal, p: Palette, run: Run, inspect: Inspect
    ) -> None:
        super().__init__()
        self.saga, self.tribunal, self.p = saga, tribunal, p
        self.run, self.inspect = run, inspect
        self.choice = choice_of(saga, tribunal)
        self.column = QVBoxLayout(self)
        self.column.setContentsMargins(0, 0, 0, 0)
        self.page: QWidget | None = None
        self.draw()

    def chosen_argument(self) -> int | None:
        return self.choice.argument

    def draw(self) -> None:
        """Lay the chapter out again from the saga and the choice."""
        if self.page is not None:
            self.column.removeWidget(self.page)
            self.page.hide()
            self.page.setParent(None)
            self.page.deleteLater()
        self.page = scrolling_page(
            self.p, self._arguments(), self._argument(), self._texts()
        )
        self.column.addWidget(self.page)

    def _choose(self, index: int) -> None:
        self.inspect(
            self.tribunal.arguments[index].topic,
            "Argument",
            pf.argument_info(self.saga, self.tribunal, index).partition("\n")[2],
        )
        if index != self.choice.argument:
            self.choice.argument = index
            self.draw()

    def _arguments(self) -> QWidget:
        p, saga, t = self.p, self.saga, self.tribunal
        chooser = Chooser()
        cards = pf.argument_cards(saga, t)
        body = ledger_rows(cards, p, chooser, self._choose)
        if self.choice.argument is not None:
            chooser.choose(self.choice.argument)
        return section(
            pf.arguments_title(t),
            p,
            body
            if cards
            else _none("No argument yet: Add one, then its polemic as a text.", p),
            buttons=verb_buttons(pf.arguments_ops(saga, t), chooser, self.run, p),
        )

    def _argument(self) -> QWidget:
        p, saga, t = self.p, self.saga, self.tribunal
        found = pf.chosen_argument(t, self.chosen_argument)
        if found is None:
            return _none("Add an argument to follow its texts and its total.", p)
        facts = [Fact(k, v) for k, v in pf.argument_facts(saga, t, found)]
        rule = TextBlock(pf.rule_text(), p)
        rule.setFont(serif(12.5))
        ops = pf.argument_ops(saga, t, self.chosen_argument)
        edit = ops.edit
        return section(
            found.topic,
            p,
            fact_grid(facts, p, 3),
            rule,
            edits={"Edit Argument": lambda: self.run(edit(0))} if edit else None,
        )

    def _texts(self) -> QWidget:
        p, saga, t = self.p, self.saga, self.tribunal
        chosen = self.chosen_argument
        chooser = Chooser()
        cards = pf.text_cards(saga, t, chosen)

        def show(row: int) -> None:
            if row < len(cards):
                found = pf.chosen_argument(t, chosen)
                under = cards[row].meta if found is not None else ""
                info = pf.text_info(saga, t, chosen, row)
                self.inspect(cards[row].title, under, info.partition("\n")[2])

        body = ledger_rows(cards, p, chooser, show)
        circulate: RowVerb = (
            pf.CIRCULATE_TITLE,
            "more",
            lambda row: pf.circulate_form(saga, t, chosen, row),
            lambda _row: True,
        )
        empty = pf.texts_grid(saga, t, chosen).empty
        return section(
            pf.texts_title(t, chosen),
            p,
            body if cards else _none(empty, p),
            buttons=verb_buttons(
                pf.texts_ops(saga, t, chosen), chooser, self.run, p, more=[circulate]
            ),
        )


def charter_strength_verbs(saga: Saga, charter: Neighbour) -> list[RowVerb]:
    """A charter's lords' Draft the Charter and Seek a Loophole buttons,
    while the saga uses the Charter Strength rule (TME p. 36)."""
    if not charter_strength.offered(saga):
        return []
    return [
        (
            charter_strength.DRAFT_TITLE,
            "more",
            lambda row: charter_strength.draft_form(saga, charter, row),
            lambda _row: True,
        ),
        (
            charter_strength.LOOPHOLE_TITLE,
            "more",
            lambda row: charter_strength.loophole_form(saga, charter, row),
            lambda _row: True,
        ),
    ]
