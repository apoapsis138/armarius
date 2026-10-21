"""The Bestiary and a creature's sheet. The Bestiary lists the saga's
creatures over the chosen one's stat block; a creature's sheet shows its
facts, then its traits, combat, powers and links. What they show is
worked out in creature_sheet.py and edited through creature_forms.py."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Button, Collapsible, Static, TabbedContent

from .... import creatures
from .... import sheet_text as st
from ....boon_hook_text import counted
from ....forms import creature as creature_forms
from ....forms import world as world_forms
from ....markup import aligned, escape, markdown_inline
from ....models import Creature, Saga
from ....sections import (
    BESTIARY_INFO_SECTION,
    BESTIARY_SECTION,
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
    LINKS_SECTION,
)
from ....sheets import creature as crs
from ....sheets.character import Fact
from ..widgets import PinnedCollapsible, SelectableList, SheetSection, TwoColumns
from .base import SheetView


def _facts_text(facts: list[Fact], column: int) -> str:
    half = (len(facts) + 1) // 2
    shown = facts[:half] if column == 0 else facts[half:]
    return aligned([(f.label, escape(f.value) or "[$label]—[/]") for f in shown])


def _list_id(section_id: str) -> str:
    return f"{section_id.removeprefix('section-')}-list"


class BestiarySheetView(SheetView):
    """The Bestiary: how many creatures, then the list of them over the
    chosen one's stat block."""

    DEFAULT_CSS = """
    BestiarySheetView #bestiary-top-panel {
        width: 1fr;
        height: auto;
    }
    """

    INITIAL_TAB = "tab-bestiary-creatures"

    def __init__(self, saga: Saga) -> None:
        super().__init__(saga)
        self.core_ops = creature_forms.bestiary_ops(saga)
        self._chosen: Creature | None = None

    def compose(self) -> ComposeResult:
        watched = (BESTIARY_INFO_SECTION, BESTIARY_SECTION)
        with (
            Vertical(id="bestiary-top-panel"),
            PinnedCollapsible(title="The Bestiary", id=BESTIARY_INFO_SECTION),
            TwoColumns(id="bestiary-info-body", text=True),
        ):
            yield self._static(watched, lambda: self._facts(0), id="bestiary-info-left")
            yield self._static(
                watched, lambda: self._facts(1), id="bestiary-info-right"
            )
        with TabbedContent(initial=self.INITIAL_TAB):
            yield self._tab("Creatures", "tab-bestiary-creatures", self._creatures_tab)

    def _facts(self, column: int) -> str:
        return _facts_text(crs.bestiary_facts(self.saga), column)

    def _creatures_tab(self) -> ComposeResult:
        saga = self.saga
        with Vertical(classes="panel-body"):
            with (
                VerticalScroll(),
                SheetSection(
                    title=self._titled(
                        BESTIARY_SECTION,
                        BESTIARY_SECTION,
                        lambda: crs.bestiary_title(saga),
                    ),
                    id=BESTIARY_SECTION,
                ),
            ):
                yield self._list(
                    BESTIARY_SECTION,
                    lambda: crs.bestiary_grid(saga).lines(),
                    id=_list_id(BESTIARY_SECTION),
                )
            yield self._panel(BESTIARY_SECTION, self._details, id="bestiary-info-panel")

    def _details(self) -> str:
        if self._chosen is not None and self._chosen not in self.saga.creatures:
            self._chosen = None
        return crs.stat_block_text(self.saga, self._chosen)

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        """A creature was chosen: show its stat block."""
        if event.selectable_list.id != _list_id(BESTIARY_SECTION):
            return
        event.stop()
        listed = creatures.listed(self.saga)
        index = event.data_index
        self._chosen = listed[index] if 0 <= index < len(listed) else None
        self.query_one("#bestiary-info-panel", Static).update(self._details())


class CreatureSheetView(SheetView):
    """A creature: its facts above four tabs, its traits, its combat, its
    powers and vis, and its description and links."""

    DEFAULT_CSS = """
    CreatureSheetView #cr-top-panel {
        width: 1fr;
        height: auto;
    }
    """

    INITIAL_TAB = "tab-cr-traits"

    def __init__(self, saga: Saga, creature: Creature) -> None:
        super().__init__(saga)
        self.creature = creature
        self.core_ops = creature_forms.creature_ops(saga, creature)

    def compose(self) -> ComposeResult:
        with (
            Vertical(id="cr-top-panel"),
            PinnedCollapsible(
                title=escape(self.creature.name), id=CREATURE_INFO_SECTION
            ),
        ):
            self._on_refresh(CREATURE_INFO_SECTION, self._refresh_title)
            with TwoColumns(id="cr-info-body", text=True):
                yield self._static(
                    CREATURE_INFO_SECTION, lambda: self._facts(0), id="cr-info-left"
                )
                yield self._static(
                    CREATURE_INFO_SECTION, lambda: self._facts(1), id="cr-info-right"
                )
            yield Button("Edit (e)", id="btn-cr-edit", compact=True)
        with TabbedContent(initial=self.INITIAL_TAB):
            yield self._tab("Traits", "tab-cr-traits", self._traits_tab)
            yield self._tab("Combat", "tab-cr-combat", self._combat_tab)
            yield self._tab("Powers & Vis", "tab-cr-powers", self._powers_tab)
            yield self._tab("Description", "tab-cr-description", self._description_tab)
            yield from self._secrets_tab(self.creature)

    def _refresh_title(self) -> None:
        panel = self.query_one(f"#{CREATURE_INFO_SECTION}", Collapsible)
        panel.title = escape(self.creature.name)

    def _facts(self, column: int) -> str:
        return _facts_text(crs.facts(self.saga, self.creature), column)

    def _section(
        self, section_id: str, title: str, rows, *, count=None
    ) -> ComposeResult:
        """A list section of the creature's, its title counting its rows
        when `count` is given."""
        with SheetSection(
            title=self._titled(
                section_id,
                section_id,
                (lambda: counted(title, count())) if count else (lambda: title),
            ),
            id=section_id,
        ):
            yield self._list(section_id, rows, id=_list_id(section_id))

    def _traits_tab(self) -> ComposeResult:
        c = self.creature
        with VerticalScroll():
            with SheetSection(
                title="Characteristics", id=CREATURE_CHARACTERISTICS_SECTION
            ):
                yield self._static(
                    CREATURE_CHARACTERISTICS_SECTION,
                    lambda: aligned(
                        [
                            ("Characteristics", escape(crs.characteristics_text(c))),
                            *((f.label, escape(f.value)) for f in crs.combat_facts(c)),
                        ]
                    ),
                    id="cr-characteristics-content",
                )
            yield from self._section(
                CREATURE_VF_SECTION,
                "Virtues, Flaws and Qualities",
                lambda: crs.vf_rows(c),
                count=lambda: len(c.virtues_flaws),
            )
            with TwoColumns(id="cr-traits-row"):
                yield from self._section(
                    CREATURE_TRAITS_SECTION,
                    "Personality Traits",
                    lambda: st.trait_rows(c.personality_traits),
                    count=lambda: len(c.personality_traits),
                )
                yield from self._section(
                    CREATURE_REPUTATIONS_SECTION,
                    "Reputations",
                    lambda: st.trait_rows(c.reputations),
                    count=lambda: len(c.reputations),
                )
            yield from self._section(
                CREATURE_ABILITIES_SECTION,
                "Abilities",
                lambda: (
                    st.ability_rows(c.abilities, c.virtues_flaws)
                    or [(None, "[$label]None yet.[/]")]
                ),
                count=lambda: len(c.abilities),
            )

    def _combat_tab(self) -> ComposeResult:
        c = self.creature
        with VerticalScroll():
            yield from self._section(
                CREATURE_ATTACKS_SECTION,
                "Combat",
                lambda: crs.attacks_grid(c).lines(),
                count=lambda: len(c.attacks),
            )
            with SheetSection(title="Health", id=CREATURE_HEALTH_SECTION):
                yield self._static(
                    (CREATURE_HEALTH_SECTION, CREATURE_INFO_SECTION),
                    self._health_text,
                    id="cr-health-content",
                )

    def _health_text(self) -> str:
        c = self.creature
        return "\n".join(
            [
                aligned(
                    [
                        ("Wound Penalties", escape(crs.wounds_text(c))),
                        ("Fatigue levels", escape(crs.fatigue_levels_text(c))),
                    ]
                ),
                *([st.wounds_text(c.wounds)] if c.can_be_wounded else []),
                *([st.fatigue_text(c.fatigue_level)] if c.tires else []),
            ]
        )

    def _powers_tab(self) -> ComposeResult:
        c = self.creature
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                yield from self._section(
                    CREATURE_POWERS_SECTION,
                    "Powers",
                    lambda: crs.powers_grid(c).lines(),
                    count=lambda: len(c.powers),
                )
                yield from self._section(
                    CREATURE_VIS_SECTION,
                    "Vis in its body",
                    lambda: crs.vis_rows(c),
                )
            yield self._panel(
                (CREATURE_POWERS_SECTION, CREATURE_INFO_SECTION),
                lambda: "[$label]Choose a power to see what it does.[/]",
                id="cr-power-info",
            )

    def _description_tab(self) -> ComposeResult:
        c = self.creature
        with VerticalScroll():
            with SheetSection(title="Description", id=CREATURE_DESCRIPTION_SECTION):
                yield self._static(
                    CREATURE_DESCRIPTION_SECTION,
                    self._description_text,
                    id="cr-description-content",
                )
            with SheetSection(
                title=self._titled(
                    LINKS_SECTION,
                    LINKS_SECTION,
                    lambda: counted("Links", len(c.links)),
                ),
                id=LINKS_SECTION,
            ):
                yield self._list(
                    LINKS_SECTION,
                    lambda: self._link_rows(),
                    id="links-list",
                )

    def _link_rows(self) -> list[tuple[int | None, str]]:
        return world_forms.link_rows(self.saga, self.creature) or [
            (None, "[$label]No links.[/]")
        ]

    def _description_text(self) -> str:
        c = self.creature
        parts = []
        for label, value in (
            ("Appearance", c.appearance),
            ("Equipment", c.equipment),
            ("Notes", c.notes),
        ):
            if value.strip():
                parts.append(f"[$label]{label}:[/] {markdown_inline(value.strip())}")
        return "\n\n".join(parts) or (
            "[$label]Nothing written yet. Edit to say what it looks like and "
            "where it lairs.[/]"
        )

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        if event.selectable_list.id != _list_id(CREATURE_POWERS_SECTION):
            return
        event.stop()
        self.query_one("#cr-power-info", Static).update(
            crs.power_text(self.creature, event.data_index)
        )
