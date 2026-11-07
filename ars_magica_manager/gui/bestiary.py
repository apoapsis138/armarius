"""The desktop's page for a creature (the saga page's Bestiary chapter
lists them as cards: pages.bestiary_chapter): its facts and Characteristics
over chapters for its traits, combat, powers and vis, and description and
links. What they say comes from sheets/creature.py; their buttons run
forms/creature.py."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from .. import artwork, creatures
from .. import sheet_text as st
from ..forms import creature as creature_forms
from ..forms import secrets as secret_forms
from ..forms import virtue as virtue_forms
from ..forms import world as world_forms
from ..grids import Grid
from ..models import Creature, Saga
from ..sections import (
    CREATURE_ABILITIES_SECTION,
    CREATURE_ATTACKS_SECTION,
    CREATURE_CHARACTERISTICS_SECTION,
    CREATURE_DESCRIPTION_SECTION,
    CREATURE_HEALTH_SECTION,
    CREATURE_INFO_SECTION,
    CREATURE_POWERS_SECTION,
    CREATURE_REPUTATIONS_SECTION,
    CREATURE_TRAITS_SECTION,
    CREATURE_VF_SECTION,
    CREATURE_VIS_SECTION,
)
from ..sheets import creature as crs
from .bookmark import with_bookmark
from .character_sheet import (
    ability_mark,
    ability_view,
    characteristic_cards,
    relations,
    secrets_chapter,
    section,
    table_section,
    trait_section,
)
from .editing import Chooser, Run, follower, verb_buttons
from .figures import fact_grid, fatigue_ladder, prose, wound_track
from .manage import RecordControls
from .pages import page_header
from .themes import Palette
from .widgets import (
    Codex,
    edit_button,
    scrolling_page,
    serif,
    table_view,
    text,
)

CHAPTERS = (
    ("Traits", "character"),
    ("Combat", "combat"),
    ("Powers & Vis", "vis"),
    ("Description", "library"),
    ("Secrets", "secrets"),
)


def _none(words: str, p: Palette) -> QWidget:
    return text(words, p["dim"], serif(12.5, italic=True), wrap=True)


class CreaturePage(QWidget):
    """A creature in the Codex layout; choosing a power or an Ability
    shows it in the inspector."""

    def __init__(
        self,
        saga: Saga,
        creature: Creature,
        p: Palette,
        run: Run = lambda _command: None,
        controls: RecordControls | None = None,
    ) -> None:
        super().__init__()
        self.saga, self.creature, self.p, self.run = saga, creature, p, run
        self.ops = creature_forms.creature_ops(saga, creature)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 12, 12, 8)
        outer.setSpacing(10)
        outer.addWidget(
            with_bookmark(self._header(), controls.bookmark(p) if controls else None)
        )
        outer.addWidget(
            fact_grid(crs.facts(saga, creature), p, 4, follow=follower(run))
        )
        outer.addWidget(
            characteristic_cards(
                creature.characteristics,
                p,
                {"intelligence": "Cunning"} if creature.cunning else None,
            )
        )
        self.codex = Codex(p)
        builders = {
            "Traits": self._traits,
            "Combat": self._combat,
            "Powers & Vis": self._powers,
            "Description": self._description,
            "Secrets": lambda: secrets_chapter(saga, creature, p, run),
        }
        for name, concept in CHAPTERS:
            if name == "Secrets":
                if secret_forms.shown(creature):
                    self.codex.add(
                        secret_forms.tab_title(creature), concept, builders[name]()
                    )
                continue
            self.codex.add(name, concept, builders[name]())
        if controls is not None:
            self.codex.add("Manage", "manage", controls.chapter(p))
        outer.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    def _edit(self, section_id: str) -> Callable[[], None]:
        edit = self.ops[section_id].edit
        assert edit is not None
        return lambda: self.run(edit(0))

    def _header(self) -> QWidget:
        p, c = self.p, self.creature
        box = QWidget()
        row = QHBoxLayout(box)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(
            page_header(c.name, crs.subtitle(c), p, creatures.icon_concept(c)), 1
        )
        buttons = QVBoxLayout()
        buttons.setSpacing(4)
        for words, section_id in (
            ("Edit", CREATURE_INFO_SECTION),
            ("Characteristics", CREATURE_CHARACTERISTICS_SECTION),
        ):
            buttons.addWidget(edit_button(words, p, self._edit(section_id)))
        buttons.addStretch(1)
        row.addLayout(buttons)
        return box

    def _grid(
        self,
        title: str,
        grid: Grid,
        section_id: str,
        inspect: Callable[[int], None] | None = None,
    ) -> QWidget:
        """`grid` as a table under `title`, with its section's Add, Edit
        and Delete acting on the row chosen."""
        p = self.p
        chooser = Chooser()

        def choose(row: int) -> None:
            chooser.choose(row)
            if inspect is not None:
                inspect(row)

        body = (
            table_view(grid.table(), p, choose) if grid.rows else _none(grid.empty, p)
        )
        buttons = verb_buttons(self.ops[section_id], chooser, self.run, p)
        return section(title, p, body, buttons=buttons)

    def _traits(self) -> QWidget:
        p, c = self.p, self.creature
        chooser = Chooser()
        vf_grid = Grid(
            ["Virtue, Flaw or Quality"],
            [[virtue_forms.vf_name(c, i)] for i in range(len(c.virtues_flaws))],
            list(range(len(c.virtues_flaws))),
            "None yet.",
        )
        vf_body = (
            table_view(vf_grid.table(), p, chooser.choose)
            if c.virtues_flaws
            else _none("None yet.", p)
        )
        abilities_chooser = Chooser()

        def show(index: object) -> None:
            assert isinstance(index, int)
            abilities_chooser.choose(index)
            ability = c.abilities[index]
            specialty = f"  ·  {ability.specialty}" if ability.specialty else ""
            self.codex.inspect(
                ability.name,
                f"{ability.category} Ability{specialty}",
                st.ability_info_text(c.abilities, index, c.virtues_flaws),
                ability_mark(ability.name, ability.category, p),
            )

        abilities = (
            ability_view(crs.ability_table(c), p, show)
            if c.abilities
            else _none("None yet.", p)
        )
        return scrolling_page(
            p,
            section(
                "Characteristics",
                p,
                fact_grid(crs.combat_facts(c), p, 2),
                edits={"Edit": self._edit(CREATURE_CHARACTERISTICS_SECTION)},
            ),
            section(
                f"Virtues, Flaws and Qualities ({len(c.virtues_flaws)})",
                p,
                vf_body,
                buttons=verb_buttons(
                    self.ops[CREATURE_VF_SECTION], chooser, self.run, p
                ),
            ),
            trait_section(
                "Personality Traits",
                c.personality_traits,
                CREATURE_TRAITS_SECTION,
                p,
                self.run,
            ),
            trait_section(
                "Reputations", c.reputations, CREATURE_REPUTATIONS_SECTION, p, self.run
            ),
            section(
                f"Abilities ({len(c.abilities)})",
                p,
                abilities,
                buttons=verb_buttons(
                    self.ops[CREATURE_ABILITIES_SECTION],
                    abilities_chooser,
                    self.run,
                    p,
                ),
            ),
        )

    def _combat(self) -> QWidget:
        p, c = self.p, self.creature
        return scrolling_page(
            p,
            self._grid(
                f"Combat ({len(c.attacks)})",
                crs.attacks_grid(c),
                CREATURE_ATTACKS_SECTION,
            ),
            section(
                "Health",
                p,
                (
                    wound_track(crs.wound_track(c), p)
                    if c.can_be_wounded
                    else _none(crs.wounds_text(c).capitalize() + ".", p)
                ),
                text("Fatigue", p["heading"], serif(12, italic=True)),
                (
                    fatigue_ladder(crs.fatigue_track(c), p)
                    if c.tires
                    else _none(crs.fatigue_levels_text(c).capitalize() + ".", p)
                ),
                fact_grid(crs.combat_facts(c)[1:], p, 2),
                edits={"Edit": self._edit(CREATURE_HEALTH_SECTION)},
            ),
        )

    def _powers(self) -> QWidget:
        p, c = self.p, self.creature

        def inspect(row: int) -> None:
            power = c.powers[row]
            symbol = artwork.art_symbol(power.form) if power.form else None
            self.codex.inspect(
                power.name,
                f"Penetration {creatures.penetration(c, power)}",
                crs.power_text(c, row),
                symbol,
            )

        vis = Grid(
            ["Vis in its body"],
            [[creatures.vis_text(v)] for v in c.vis],
            list(range(len(c.vis))),
            "No vis in its body.",
        )
        return scrolling_page(
            p,
            self._grid(
                f"Powers ({len(c.powers)})",
                crs.powers_grid(c),
                CREATURE_POWERS_SECTION,
                inspect,
            ),
            self._grid("Vis in its body", vis, CREATURE_VIS_SECTION),
        )

    def _description(self) -> QWidget:
        p, c = self.p, self.creature
        parts: list[QWidget] = []
        for label, value in (
            ("Appearance", c.appearance),
            ("Equipment", c.equipment),
            ("Notes", c.notes),
        ):
            if value.strip():
                parts.append(text(label, p["heading"], serif(12, italic=True)))
                parts.append(prose(value.strip(), p, initial=False))
        return scrolling_page(
            p,
            section(
                "Description",
                p,
                *(parts or [_none("Nothing written yet.", p)]),
                edits={"Edit": self._edit(CREATURE_DESCRIPTION_SECTION)},
            ),
            *relations(self.saga, c, p, self.run, links=False),
            table_section(
                f"Links ({len(c.links)})",
                world_forms.link_table(self.saga, c),
                self.ops[world_forms.LINKS_SECTION],
                p,
                self.run,
                empty="No links.",
            ),
        )
