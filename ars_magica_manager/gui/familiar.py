"""The desktop familiar page in the Codex layout: a header
with the name, whose familiar it is, its Size, Soak and Magic Resistance
and its Magic Might as a seal, over its Characteristics; then chapters
for its bond and Cords (each in its metal), Virtues and Flaws, combat and health, Abilities
and Bond Powers, with the inspector beside them.

What it says comes from the shared core (sheets/familiar.py and
familiars.py), as the terminal's familiar sheet does, and its Edit, Add
and Delete buttons run the core's forms (forms/familiar.py and
forms/trait.py).
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .. import artwork
from .. import familiars as fam
from .. import sheet_text as st
from ..forms import familiar as ff
from ..forms import virtue as virtue_forms
from ..models import Familiar, Saga
from ..sheets import familiar as fs
from .character_sheet import (
    ability_mark,
    ability_view,
    characteristic_cards,
    section,
    side_by_side,
    trait_section,
    vf_card,
)
from .editing import Chooser, Run, choose_cards, verb_buttons
from .figures import (
    CordFigure,
    Seal,
    fact_grid,
    fatigue_ladder,
    wound_track,
)
from .manage import RecordControls
from .pages import card_grid, card_title, symbol_label
from .themes import Palette
from .widgets import (
    Card,
    ClickableCard,
    Codex,
    badge,
    cells_table,
    display_name,
    edit_button,
    mix,
    scrolling_page,
    serif,
    text,
)

CHAPTERS = (
    ("Identity & Cords", "familiar"),
    ("Virtues & Flaws", "magic"),
    ("Combat & Health", "combat"),
    ("Abilities", "library"),
    ("Bond Powers", "enchanted_item"),
)


def _none(words: str, p: Palette) -> QLabel:
    return text(words, p["dim"], serif(12.5, italic=True))


class FamiliarPage(QWidget):
    """A familiar in the Codex layout; choosing anything shows it in the
    inspector."""

    def __init__(
        self,
        saga: Saga,
        familiar: Familiar,
        p: Palette,
        run: Run = lambda _command: None,
        controls: RecordControls | None = None,
    ) -> None:
        super().__init__()
        self.saga, self.familiar, self.p = saga, familiar, p
        self.run = run
        self.edits = ff.edits(familiar)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 12, 12, 8)
        outer.setSpacing(10)
        outer.addWidget(self._header())
        outer.addWidget(characteristic_cards(familiar.characteristics, p))
        self.codex = Codex(p)
        self.inspector = self.codex.inspector
        builders = {
            "Identity & Cords": self._identity,
            "Virtues & Flaws": self._virtues_flaws,
            "Combat & Health": self._combat,
            "Abilities": self._abilities,
            "Bond Powers": self._powers,
        }
        for name, concept in CHAPTERS:
            self.codex.add(name, concept, builders[name]())
        if controls is not None:
            self.codex.add("Manage", "manage", controls.chapter(p))
        outer.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    def inspect(self, title: str, subtitle: str, markup: str, symbol=None) -> None:
        self.codex.inspect(title, subtitle, markup, symbol)

    def _edit(self, *names: str, label: str = "Edit") -> dict[str, Callable[[], None]]:
        """Edit buttons for the forms `names`: one called `label`, or one
        per form named for it."""
        return {
            (label if len(names) == 1 else name): (
                lambda form=self.edits[name]: self.run(form)
            )
            for name in names
        }

    # Above the chapters

    def _header(self) -> QWidget:
        p, f = self.p, self.familiar
        box = QWidget()
        row = QHBoxLayout(box)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(14)
        row.addWidget(
            symbol_label(artwork.icon("familiar"), p, 56), 0, Qt.AlignmentFlag.AlignTop
        )
        names = QVBoxLayout()
        names.setSpacing(0)
        names.addWidget(display_name(f.name or "(unnamed)", p))
        names.addWidget(
            text(fs.subtitle(self.saga, f), p["label"], serif(12.5, italic=True))
        )
        row.addLayout(names)
        row.addStretch(1)
        row.addWidget(fact_grid(fs.header_facts(f), p, 2))
        row.addSpacing(10)
        pool = fs.might_pool(f)
        row.addWidget(
            Seal(
                str(f.magic_might),
                "Magic Might",
                p["realm-Magic"],
                f"Magic Might {f.magic_might}" + (f": {pool}" if pool else ""),
                p,
            )
        )
        buttons = QVBoxLayout()
        buttons.setSpacing(4)
        for words, form in (
            ("Edit", self.edits["Familiar"]),
            ("Characteristics", self.edits["Characteristics"]),
        ):
            button = edit_button(words, p, lambda form=form: self.run(form))
            button.setToolTip(form.title)
            buttons.addWidget(button)
        buttons.addStretch(1)
        row.addLayout(buttons)
        return box

    # Chapters

    def _identity(self) -> QWidget:
        """How the bond was made, its three Cords, and the familiar's
        Personality Traits and Reputations."""
        p, f = self.p, self.familiar
        cords = []
        for cord in fs.cords(f):
            metal = p[f"cord-{cord.name.split()[0].lower()}"]
            card = Card(p, pad=10, edge=metal)
            top = QHBoxLayout()
            top.addWidget(text(cord.name, p["foreground"], serif(13.5, bold=True)))
            top.addStretch(1)
            top.addWidget(
                text(
                    f"+{cord.score}",
                    mix(metal, p["foreground"], 0.3).name(),
                    serif(16, bold=True),
                )
            )
            card.column.addLayout(top)
            card.column.addWidget(CordFigure(cord.score, metal, p))
            card.column.addWidget(text(cord.effect, p["label"], wrap=True))
            card.column.addStretch(1)
            card.column.addWidget(
                text(f"{cord.cost} points", p["dim"], serif(10, caps=True))
            )
            cords.append(card)
        return scrolling_page(
            p,
            section(
                "The Bond",
                p,
                fact_grid(fs.binding_facts(f), p, 4),
                edits=self._edit("Binding & Cords"),
            ),
            section("Cords", p, card_grid(cords, 3)),
            # One above the other: side by side, their buttons would make
            # the chapter wider than the space beside the inspector.
            trait_section(
                "Personality Traits",
                f.personality_traits,
                "section-fam-personality-traits",
                p,
                self.run,
            ),
            trait_section(
                "Reputations",
                f.reputations,
                "section-fam-reputations",
                p,
                self.run,
            ),
        )

    def _virtues_flaws(self) -> QWidget:
        p, f = self.p, self.familiar
        columns = []
        for side, tone in (("Virtue", "text-success"), ("Flaw", "text-error")):
            column = QWidget()
            stack = QVBoxLayout(column)
            stack.setContentsMargins(0, 0, 0, 0)
            stack.setSpacing(10)
            points = fs.vf_points(f, side)
            chooser = Chooser()
            cards = [
                vf_card(
                    card,
                    p[tone],
                    p,
                    lambda card=card: self.inspect(
                        card.name,
                        f"{card.tier}  ·  {card.category}",
                        fam.vf_info_text(f, card.index),
                    ),
                )
                for card in fs.vf_cards(f, side)
            ]
            choose_cards(cards, chooser)
            stack.addWidget(
                section(
                    f"{side}s  ·  {points:g} points",
                    p,
                    *cards,
                    buttons=verb_buttons(
                        virtue_forms.virtue_flaw_ops(self.saga, f, side),
                        chooser,
                        self.run,
                        p,
                    ),
                )
            )
            stack.addStretch(1)
            columns.append(column)
        return scrolling_page(p, side_by_side(*columns, spacing=18))

    def _combat(self) -> QWidget:
        """The wounds it has on its Size's Damage Table, its Fatigue, and
        its natural weapons."""
        p, f = self.p, self.familiar
        weapons = fs.natural_weapons(f)
        chooser = Chooser()

        def choose(row: int) -> None:
            chooser.choose(row)
            self.inspect(
                weapons.rows[row][0],
                "Natural Weapon",
                fam.natural_weapon_info_text(f, row),
            )

        self.weapons = cells_table(weapons.columns, weapons.rows, p, choose)
        return scrolling_page(
            p,
            section(
                "Health",
                p,
                wound_track(fs.wound_track(f), p),
                text("Fatigue", p["heading"], serif(12, italic=True)),
                fatigue_ladder(fs.fatigue_track(f), p),
                fact_grid(fs.health_facts(f), p, 4),
                edits=self._edit("Wounds", "Fatigue"),
            ),
            section(
                f"Natural Weapons & Attacks ({len(f.natural_weapons)})",
                p,
                self.weapons if f.natural_weapons else _none("None recorded.", p),
                buttons=verb_buttons(ff.natural_weapon_ops(f), chooser, self.run, p),
            ),
        )

    def _abilities(self) -> QWidget:
        p, f = self.p, self.familiar
        chooser = Chooser()

        def show(index: object) -> None:
            assert isinstance(index, int)
            chooser.choose(index)
            ability = f.abilities[index]
            specialty = f"  ·  {ability.specialty}" if ability.specialty else ""
            self.inspect(
                ability.name,
                f"{ability.category} Ability{specialty}",
                st.ability_info_text(f.abilities, index, f.virtues_flaws),
                ability_mark(ability.name, ability.category, p),
            )

        self.ability_table = ability_view(fs.ability_table(f), p, show)
        return scrolling_page(
            p,
            section(
                f"Abilities ({len(f.abilities)})",
                p,
                text(
                    "Shares its magus's Language scores.",
                    p["label"],
                    serif(12, italic=True),
                ),
                self.ability_table,
                buttons=verb_buttons(
                    ff.ability_ops(self.saga, f), chooser, self.run, p
                ),
            ),
        )

    def _powers(self) -> QWidget:
        """Each Bond Power as a card with its Form's symbol."""
        p, f = self.p, self.familiar
        cards = []
        for power in fs.bond_power_cards(f):
            form = artwork.art_symbol(power.form) if power.form else None
            card = ClickableCard(p, pad=12)
            card_title(
                card,
                power.name,
                power.arts or "No Arts set",
                p,
                symbol_label(form, p, 36)
                if form
                else symbol_label(artwork.icon("enchanted_item"), p, 32),
            )
            figures = QHBoxLayout()
            figures.addWidget(badge(f"Level {power.level}", p["accent"], p))
            figures.addWidget(
                text(
                    f"{power.uses_per_day} a day  ·  Penetration {power.penetration}",
                    p["label"],
                )
            )
            figures.addStretch(1)
            card.column.addLayout(figures)
            card.clicked = (
                lambda index=power.index, name=power.name, arts=(power.arts): (
                    self.inspect(
                        name,
                        arts,
                        fam.bond_power_info_text(f, index),
                        artwork.art_symbol(f.bond_powers[index].form)
                        if f.bond_powers[index].form
                        else None,
                    )
                )
            )
            cards.append(card)
        chooser = Chooser()
        choose_cards(cards, chooser)
        return scrolling_page(
            p,
            section(
                f"Bond Powers ({len(cards)})",
                p,
                card_grid(cards, 2) if cards else _none("None yet.", p),
                buttons=verb_buttons(ff.bond_power_ops(f), chooser, self.run, p),
            ),
        )
