"""The Character sheet."""

from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.widgets import (
    Button,
    Collapsible,
    Static,
    TabbedContent,
)

from .... import books as bk
from .... import casting_text, seasons, tradition_text, traditions
from .... import enchanted_devices as ed
from .... import lab_texts as lt
from .... import laboratories as lab_text
from .... import research_text as rt
from .... import saga_overview as ov
from .... import sheet_text as st
from ....arts import FORMS, TECHNIQUES
from ....boon_hook_text import counted, match_colour, points_title
from ....forms import agents as agent_forms
from ....forms import constant_effect as constant_forms
from ....forms import power as power_forms
from ....forms import tradition as tradition_forms
from ....forms.secrets import secrets_ops
from ....markup import escape
from ....models import (
    LINE,
    Character,
    Saga,
    TraditionDef,
)
from ....rules import activities as season_rules
from ....rules import creation_virtues as cv
from ....rules import library
from ....sections import AGENTS_SECTION, CONSTANT_EFFECTS_SECTION, POWERS_SECTION
from ....sections import CHAR_AHEAD_SECTION as AHEAD_SECTION
from ....sections import CHAR_CALENDAR_SECTION as CALENDAR_SECTION
from ....sheets import character as cs
from ....traditions import tradition_list, tradition_section, tradition_tab
from ..widgets import (
    DetailsPanel,
    PinnedCollapsible,
    SelectableList,
    SheetSection,
    TableHeader,
    TwoColumns,
)
from .base import SheetView
from .lists import BookListView

#: What the Research Log is read from: the goals, and the log itself.
RESEARCH_SECTIONS = ("section-research-goals", "section-research-log")

#: The Agents list and its details panel.
AGENTS_LIST = "char-agents-list"
AGENTS_INFO = "char-agents-info"
#: What the Agents header reads besides the agents: the limit's
#: Presence, Intrigue, Leadership and the Gift, and the Agency
#: experience a season brings.
AGENTS_SOURCES = (
    AGENTS_SECTION,
    "section-char-characteristics",
    "tab-abilities",
    "section-vf-virtues",
    "section-vf-flaws",
)

#: The Seasons Ahead list and the chosen season's plan under it.
AHEAD_LIST = "char-ahead-list"
AHEAD_INFO = "char-ahead-info"


class CharacterSheetView(SheetView):
    """The character sheet mounted into WorkspaceScreen's detail pane.

    A fixed top panel (Info above Characteristics -- not inside any tab,
    permanently expanded, same PinnedCollapsible pattern as
    CovenantSheetView/LaboratorySheetView) above the tabbed body. Tab
    order: Description, Abilities,
    Virtues & Flaws, Hermetic Magic and Research (magi only), Inventory,
    Agents, Planning, Diary.
    (A magus's Lab Totals are on their laboratory's sheet.)

    - Description (tab, id "tab-description"): Hermetic Background (magi
      only), Biographical Detail (merged Background + Description + the
      new Biography field), Personality Traits and Reputations (side by
      side), Aging & Warping, Health (merged Wounds + Fatigue, two
      columns, two independent Edit affordances).
    - Abilities (tab, id "tab-abilities"): a flat pane (no Collapsible)
      with the Abilities list and its details panel.
    - Virtues & Flaws (tab, id "tab-vf"): Virtues and Flaws as two
      independently-collapsible sections side by side (mirroring
      CovenantSheetView's Boons/Hooks), with one details panel below both,
      separate from either section.
    - Hermetic Magic (tab, id "tab-hermetic", magi only): Magical Arts
      (a SheetSection like the tab's others, open by default -- two side-by-
      side selectable columns, Techniques then Forms, each row Name/Level/
      XP; 'e' still opens EditArtsScreen to edit every Art at once), Raw
      Vis (the first of two duplicated instances, both backed by
      character.raw_vis and both mounted at once -- refresh_section()
      updates both lists regardless of which section id triggered it, so
      switching tabs never shows stale data), and Known Spells (folded in
      from the old "Spells" tab). The three lists (Techniques, Forms,
      Known Spells) share one details panel docked at the tab's bottom,
      outside every section -- see _refresh_hermetic_info().
    - Research (tab, id "tab-research", magi only): Research Goals and the
      Research Log of every season's work toward them, newest first, over
      one details panel: the chosen goal's stage, steps and odds, or the
      chosen season's roll on the chart -- see _refresh_research_info().
    - Inventory (tab, id "tab-inventory"): Raw Vis (magi only, the second
      of the two duplicated instances -- see Hermetic Magic above),
      Personal Gear (renamed from "Inventory", same character.inventory
      data), Books.
    - Agents (tab, id "tab-agents"): the limit, the people won and being
      won, and the chosen one's details panel (forms/agents.py).
    - Planning (tab, id "tab-planning", every character type): This Season,
      the season's plan and what it will give; a grog's
      says grogs are updated yearly. Then the Seasons Ahead and the
      Calendar, a line per year, each planned season with its result.
    - Diary (tab, id "tab-diary", every character type): a flat pane like
      the laboratory's Diary -- the entries written as seasons are applied
      (editable), with the details panel docked below. In
      _CHARACTER_DISPATCH_TABS, so a / e / d act on it.
    """

    DEFAULT_CSS = """
    CharacterSheetView #char-top-panel {
        width: 1fr;
        height: auto;
    }

    CharacterSheetView .arts-col-title {
        text-style: bold;
    }
    """

    def __init__(self, saga: Saga, character: Character) -> None:
        super().__init__(saga)
        self.character = character
        self.core_ops = secrets_ops(character)
        if cs.has_statblock(character):
            self.INITIAL_TAB = "tab-statblock"

    @property
    def creation_record(self) -> Character:
        return self.character

    INITIAL_TAB = "tab-description"

    def compose(self) -> ComposeResult:
        character = self.character
        yield from self._top_panel()
        # A Line or Sketch character opens on its statblock and leaves out
        # what only play needs; a Line one has only who they are.
        sketch = cs.has_statblock(character)
        scores = character.detail != LINE
        with TabbedContent(initial=self.INITIAL_TAB):
            if sketch:
                yield self._tab(
                    "Statblock", "tab-statblock", self._scrolling(self._statblock_tab)
                )
            yield self._tab("Description", "tab-description", self._description_tab)
            if scores:
                yield self._tab("Abilities", "tab-abilities", self._abilities_tab)
                yield self._tab("Virtues & Flaws", "tab-vf", self._virtues_flaws_tab)
            if scores and character.type == "magus":
                yield self._tab("Hermetic Magic", "tab-hermetic", self._hermetic_tab)
                if not sketch:
                    yield self._tab("Research", "tab-research", self._research_tab)
            if scores:
                for tradition in traditions.of(character):
                    yield self._tab(
                        tradition.title,
                        tradition_tab(tradition.id),
                        lambda t=tradition: self._tradition_tab(t),
                    )
            if not sketch:
                yield self._tab("Inventory", "tab-inventory", self._inventory_tab)
                yield self._tab("Agents", "tab-agents", self._agents_tab)
                yield self._tab(
                    "Planning", "tab-planning", self._scrolling(self._planning_tab)
                )
            yield self._tab("Diary", "tab-diary", self._diary_tab)
            yield from self._secrets_tab(character)

    #: Every section a statblock summarises: it is redrawn when one changes.
    _STATBLOCK_SOURCES = (
        "section-char-info",
        "section-char-characteristics",
        "tab-abilities",
        "section-vf-virtues",
        "section-vf-flaws",
        "section-arts",
        "section-known-spells",
        "section-personality-traits",
        "section-reputations",
    )

    def _statblock_tab(self) -> ComposeResult:
        """A Line or Sketch character as the books print an NPC. Each part
        is edited where it lives: the top panel, or its own tab."""
        with SheetSection(title="Statblock", id="section-char-statblock"):
            yield self._static(
                self._STATBLOCK_SOURCES,
                lambda: cs.statblock_text(self.saga, self.character),
                id="char-statblock",
            )

    def _abilities_tab(self) -> ComposeResult:
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                yield self._list(
                    "tab-abilities", self._ability_rows, id="abilities-list"
                )
            yield self._panel(
                "tab-abilities",
                lambda: self._ability_info_text(None),
                id="ability-info",
            )

    def _tradition_tab(self, tradition: TraditionDef) -> ComposeResult:
        """A tradition's chapter: its Arts and Abilities the character has,
        grouped by the part they play, and the chosen one's details."""
        section = tradition_section(tradition.id)
        # The casting, defenses and seasons text reads the Arts, the bound
        # beings, the Characteristics, the Virtues and the covenant's aura.
        sources = (
            section,
            traditions.bonds_section(tradition.id),
            "section-char-info",
            "section-char-characteristics",
            "tab-abilities",
            "section-vf-virtues",
            "section-vf-flaws",
        )
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                with SheetSection(title="Arts and Abilities", id=section):
                    yield self._list(
                        section,
                        lambda: st.grouped_ability_rows(
                            self.character.abilities,
                            traditions.chapter_groups(self.character, tradition),
                            self.character.virtues_flaws,
                        ),
                        id=tradition_list(tradition.id),
                    )
                effects = traditions.effects_section(tradition.id)
                self.core_ops[effects] = tradition_forms.effect_ops(
                    self.character, tradition
                )
                with SheetSection(title="Effects and Items", id=effects):
                    yield self._list(
                        (effects, *sources),
                        lambda: tradition_text.effect_rows(
                            self.saga, self.character, tradition
                        ),
                        id=traditions.effects_list(tradition.id),
                    )
                bonds = traditions.bonds_section(tradition.id)
                self.core_ops[bonds] = tradition_forms.bond_ops(
                    self.saga, self.character, tradition
                )
                with SheetSection(title="Bound Beings", id=bonds):
                    yield self._list(
                        bonds,
                        lambda: tradition_text.bond_rows(self.character, tradition),
                        id=traditions.bonds_list(tradition.id),
                    )
                    yield self._static(
                        bonds,
                        lambda: tradition_text.bonds_text(tradition),
                        id=f"trad-{tradition.id}-bond-rules",
                    )
                with SheetSection(
                    title="Casting", id=traditions.casting_section(tradition.id)
                ):
                    yield self._static(
                        sources,
                        lambda: tradition_text.casting_text(
                            self.saga, self.character, tradition
                        ),
                        id=f"trad-{tradition.id}-casting",
                    )
                with SheetSection(
                    title="Magical Defenses",
                    id=traditions.defenses_section(tradition.id),
                ):
                    yield self._static(
                        sources,
                        lambda: tradition_text.defenses_text(self.character, tradition),
                        id=f"trad-{tradition.id}-defenses",
                    )
                with SheetSection(
                    title="Seasons", id=traditions.seasons_section(tradition.id)
                ):
                    yield self._static(
                        sources,
                        lambda: tradition_text.seasons_text(
                            self.saga, self.character, tradition
                        ),
                        id=f"trad-{tradition.id}-seasons",
                    )
                with SheetSection(
                    title="Warping", id=traditions.warping_section(tradition.id)
                ):
                    yield self._static(
                        (*sources, "section-aging"),
                        lambda: tradition_text.warping_text(
                            self.saga, self.character, tradition
                        ),
                        id=f"trad-{tradition.id}-warping",
                    )
                if tradition.pools:
                    pools = traditions.pools_section(tradition.id)
                    self.core_ops[pools] = tradition_forms.pool_ops(
                        self.character, tradition
                    )
                    with SheetSection(title="Pools", id=pools):
                        yield self._static(
                            pools,
                            lambda: tradition_text.pools_text(
                                self.character, tradition
                            ),
                            id=f"trad-{tradition.id}-pools",
                        )
            yield self._panel(
                section,
                lambda: self._ability_info_text(None),
                id=f"trad-{tradition.id}-info",
            )

    def selected_tradition_ability(self, tradition_id: str) -> int | None:
        """Index into character.abilities of the row chosen in a
        tradition's chapter, or None."""
        try:
            chosen = self.query_one(f"#{tradition_list(tradition_id)}", SelectableList)
        except NoMatches:
            return None
        return chosen.selected_data_index

    def _diary_tab(self) -> ComposeResult:
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                yield self._list(
                    "tab-diary",
                    lambda: lab_text.diary_rows(self.character.diary),
                    id="char-diary-list",
                )
            yield self._panel(
                "tab-diary",
                lambda: lab_text.diary_info_text(self.character.diary, None),
                id="char-diary-info",
            )

    def _planning_tab(self) -> ComposeResult:
        """This Season: the season's plan and what it will give; then the
        Seasons Ahead, the rest of the year, each planned the same way."""
        planned = ("section-char-season", AHEAD_SECTION)
        with SheetSection(
            title=self._titled(
                "section-char-season",
                "section-char-season",
                lambda: (
                    f"This Season ({self.saga.current_season} {self.saga.current_year})"
                ),
            ),
            id="section-char-season",
        ):
            yield self._static(
                planned,
                lambda: seasons.plan_text(self.saga, self.character),
                id="char-season-content",
            )
        ahead = SheetSection(
            title=self._titled(
                planned, AHEAD_SECTION, lambda: seasons.ahead_title(self.saga)
            ),
            id=AHEAD_SECTION,
        )
        # A grog's yearly update covers the year: no seasons ahead. The type
        # can change on any section's edit.
        ahead.display = season_rules.is_planned(self.character)
        self._on_refresh_matching(
            lambda _section: True,
            lambda: setattr(ahead, "display", season_rules.is_planned(self.character)),
        )
        with ahead:
            yield self._list(
                planned,
                lambda: seasons.ahead_rows(self.saga, self.character),
                id=AHEAD_LIST,
            )
            yield self._static(
                planned,
                lambda: seasons.ahead_info(
                    self.saga, self.character, self.selected_season_ahead()
                ),
                id=AHEAD_INFO,
            )
        calendar = SheetSection(
            title="Calendar",
            id=CALENDAR_SECTION,
        )
        calendar.display = season_rules.is_planned(self.character)
        self._on_refresh_matching(
            lambda _section: True,
            lambda: setattr(
                calendar, "display", season_rules.is_planned(self.character)
            ),
        )
        with calendar:
            yield self._static(
                (*planned, "tab-diary", CALENDAR_SECTION),
                lambda: ov.calendar_text(self.saga, self.character),
                id="char-calendar-content",
            )

    def selected_season_ahead(self) -> int | None:
        """Index into seasons.seasons_ahead of the chosen row, or None."""
        try:
            return self.query_one(f"#{AHEAD_LIST}", SelectableList).selected_data_index
        except NoMatches:
            return None

    def selected_diary_entry(self) -> int | None:
        """Index into character.diary of the chosen row, or None."""
        return self.query_one("#char-diary-list", SelectableList).selected_data_index

    def _top_panel(self) -> ComposeResult:
        """The always-visible info and Characteristics panels above the
        tabs."""
        character = self.character
        with Vertical(id="char-top-panel"):
            with PinnedCollapsible(
                title=escape(character.name), id="section-char-info"
            ):
                with TwoColumns(id="char-info-body", text=True):
                    yield self._static(
                        "section-char-info", self._info_left_text, id="char-info-left"
                    )
                    yield self._static(
                        "section-char-info",
                        self._info_right_text,
                        id="char-info-right",
                    )
                yield from self._top_buttons("btn-char-info-edit")
            self._on_refresh("section-char-info", self._refresh_title)
            with PinnedCollapsible(
                title="Characteristics", id="section-char-characteristics"
            ):
                yield self._static(
                    "section-char-characteristics",
                    self._characteristics_text,
                    id="char-characteristics-content",
                )
                yield Button(
                    "Edit (e)", id="btn-char-characteristics-edit", compact=True
                )

    def _refresh_title(self) -> None:
        self.query_one("#section-char-info", Collapsible).title = escape(
            self.character.name
        )

    def _description_tab(self) -> ComposeResult:
        """Hermetic Background (magi), Biographical Detail, Personality
        Traits and Reputations, Connections, Aging & Warping, and Health."""
        character = self.character
        with VerticalScroll():
            if character.type == "magus":
                with (
                    SheetSection(
                        title="Hermetic Background",
                        id="section-hermetic-background",
                    ),
                    TwoColumns(id="hermetic-background-row", text=True),
                ):
                    yield self._static(
                        "section-hermetic-background",
                        self._hermetic_background_left_text,
                        id="hermetic-background-left",
                    )
                    with Vertical(id="hermetic-background-right-col"):
                        yield self._static(
                            "section-hermetic-background",
                            self._hermetic_background_right_text,
                            id="hermetic-background-right",
                        )
                        yield Button(
                            "Lab Texts Read",
                            id="btn-char-lab-text-access",
                            compact=True,
                        )
            with (
                SheetSection(
                    title="Biographical Detail", id="section-char-biographical"
                ),
                TwoColumns(id="char-biographical-row", text=True),
            ):
                yield self._static(
                    "section-char-biographical",
                    self._biographical_left_text,
                    id="char-biographical-left",
                )
                yield self._static(
                    "section-char-biographical",
                    self._biographical_right_text,
                    id="char-biographical-right",
                )
            with TwoColumns(id="pt-rep-row"):
                with SheetSection(
                    title=self._titled(
                        "section-personality-traits",
                        "section-personality-traits",
                        lambda: counted(
                            "Personality Traits",
                            len(self.character.personality_traits),
                        ),
                    ),
                    id="section-personality-traits",
                ):
                    yield self._list(
                        "section-personality-traits",
                        self._personality_trait_rows,
                        id="personality-traits-list",
                    )
                with SheetSection(
                    title=self._titled(
                        "section-reputations",
                        "section-reputations",
                        lambda: counted("Reputations", len(self.character.reputations)),
                    ),
                    id="section-reputations",
                ):
                    yield self._list(
                        "section-reputations",
                        self._reputation_rows,
                        id="character-reputations-list",
                    )
            yield from self._connections(character)
            with SheetSection(title="Aging & Warping", id="section-aging"):
                yield self._static(
                    ("section-aging", CONSTANT_EFFECTS_SECTION),
                    self._aging_text,
                    id="aging-content",
                )
            self.core_ops[CONSTANT_EFFECTS_SECTION] = constant_forms.ops(
                self.saga, self.character
            )
            with SheetSection(
                title=self._titled(
                    CONSTANT_EFFECTS_SECTION,
                    CONSTANT_EFFECTS_SECTION,
                    lambda: constant_forms.title(self.character),
                ),
                id=CONSTANT_EFFECTS_SECTION,
            ):
                yield self._list(
                    (CONSTANT_EFFECTS_SECTION, "section-aging"),
                    lambda: constant_forms.rows(self.character),
                    id="char-constant-effects-list",
                )
            with (
                SheetSection(title="Health", id="section-char-health"),
                TwoColumns(id="char-health-row", text=True),
            ):
                with Vertical(id="char-health-wounds-col"):
                    yield self._static(
                        "section-char-health", self._wounds_text, id="wounds-content"
                    )
                    yield Button(
                        "Edit Wounds (e)",
                        id="btn-char-health-wounds-edit",
                        compact=True,
                    )
                with Vertical(id="char-health-fatigue-col"):
                    yield self._static(
                        "section-char-health", self._fatigue_text, id="fatigue-content"
                    )
                    yield Button(
                        "Edit Fatigue",
                        id="btn-char-health-fatigue-edit",
                        compact=True,
                    )

    def _virtues_flaws_tab(self) -> ComposeResult:
        """The Virtue and Flaw lists side by side, and the details panel."""
        vf_sections = ("section-vf-virtues", "section-vf-flaws")
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                with TwoColumns(id="vf-row"):
                    with SheetSection(
                        title=self._titled(
                            vf_sections,
                            "section-vf-virtues",
                            lambda: self._vf_title("Virtue"),
                        ),
                        id="section-vf-virtues",
                    ):
                        yield self._list(
                            vf_sections,
                            lambda: self._vf_rows("Virtue"),
                            id="vf-virtues-list",
                            group="vf",
                        )
                    with SheetSection(
                        title=self._titled(
                            vf_sections,
                            "section-vf-flaws",
                            lambda: self._vf_title("Flaw"),
                        ),
                        id="section-vf-flaws",
                    ):
                        yield self._list(
                            vf_sections,
                            lambda: self._vf_rows("Flaw"),
                            id="vf-flaws-list",
                            group="vf",
                        )
                self.core_ops[POWERS_SECTION] = power_forms.ops(self.character)
                with SheetSection(
                    title=self._titled(
                        POWERS_SECTION,
                        POWERS_SECTION,
                        lambda: power_forms.title(self.character),
                    ),
                    id=POWERS_SECTION,
                ):
                    yield self._list(
                        POWERS_SECTION,
                        lambda: power_forms.rows(self.character),
                        id="char-powers-list",
                        group="vf",
                    )
            yield self._panel(
                vf_sections, lambda: self._vf_info_text(None), id="vf-info"
            )

    #: Raw Vis deliberately appears twice (Hermetic Magic and Inventory tabs),
    #: both backed by character.raw_vis and both mounted at once
    #: (TabbedContent keeps inactive panes mounted, just hidden): either
    #: section id refreshes both lists, so neither goes stale.
    _RAW_VIS_SECTIONS = ("section-raw-vis-hermetic", "section-raw-vis-inventory")
    #: The Hermetic Magic details panel with nothing chosen.
    _HERMETIC_INFO_PLACEHOLDER = (
        "[dim]Select an Art or a Known Spell to see its details.[/]"
    )

    def _hermetic_tab(self) -> ComposeResult:
        """Magical Arts, Raw Vis and Known Spells (scrolling), and the
        details panel docked below them. Magi only."""
        with Vertical(id="hermetic-body", classes="panel-body"):
            with VerticalScroll(id="hermetic-scroll"):
                yield self._static(
                    ("section-char-devices", "section-arts"),
                    lambda: ed.talisman_line(self.saga, self.character),
                    id="hermetic-talisman",
                )
                with (
                    SheetSection(title="Magical Arts", id="section-arts"),
                    TwoColumns(id="arts-row"),
                ):
                    with Vertical(id="arts-techniques-col"):
                        yield Static("Techniques", classes="arts-col-title")
                        yield TableHeader(self._arts_header_text())
                        yield self._list(
                            "section-arts",
                            lambda: self._arts_rows(TECHNIQUES),
                            id="arts-techniques-list",
                            group="hermetic",
                        )
                    with Vertical(id="arts-forms-col"):
                        yield Static("Forms", classes="arts-col-title")
                        yield TableHeader(self._arts_header_text())
                        yield self._list(
                            "section-arts",
                            lambda: self._arts_rows(FORMS),
                            id="arts-forms-list",
                            group="hermetic",
                        )
                with SheetSection(title="Casting Scores", id="section-casting"):
                    yield self._static(
                        ("section-casting", "section-arts", "section-char-info"),
                        lambda: casting_text.casting_scores_text(
                            self.saga, self.character
                        ),
                        id="casting-scores",
                    )
                with SheetSection(title="Raw Vis", id="section-raw-vis-hermetic"):
                    yield self._list(
                        self._RAW_VIS_SECTIONS,
                        self._raw_vis_rows,
                        id="raw-vis-list-hermetic",
                    )
                with SheetSection(
                    title=self._titled(
                        "section-known-spells",
                        "section-known-spells",
                        lambda: counted(
                            "Known Spells", len(self.character.spells_known)
                        ),
                    ),
                    id="section-known-spells",
                ):
                    yield self._list(
                        "section-known-spells",
                        self._known_spell_rows,
                        id="known-spells-list",
                        group="hermetic",
                    )
            yield DetailsPanel(self._HERMETIC_INFO_PLACEHOLDER, id="hermetic-info")
            self._on_refresh(
                ("section-arts", "section-known-spells"),
                self._refresh_hermetic_info,
            )

    #: The Research tab's details panel with nothing chosen.
    _RESEARCH_INFO_PLACEHOLDER = (
        "[dim]Select a research goal or a season of its log to see its details.[/]"
    )

    def _research_tab(self) -> ComposeResult:
        """Research Goals and the Research Log of every season's work
        toward them (scrolling), over the chosen goal's or season's details.
        Magi only."""
        with Vertical(id="research-body", classes="panel-body"):
            with VerticalScroll(id="research-scroll"):
                with SheetSection(
                    title=self._titled(
                        "section-research-goals",
                        "section-research-goals",
                        lambda: counted(
                            "Research Goals", len(self.character.breakthroughs)
                        ),
                    ),
                    id="section-research-goals",
                ):
                    yield self._list(
                        "section-research-goals",
                        self._research_goal_rows,
                        id="research-goals-list",
                        group="research",
                    )
                with SheetSection(
                    title=self._titled(
                        RESEARCH_SECTIONS,
                        "section-research-log",
                        lambda: counted(
                            "Research Log", len(rt.log_entries(self.character))
                        ),
                    ),
                    id="section-research-log",
                ):
                    yield TableHeader(rt.LOG_HEADER)
                    yield self._list(
                        RESEARCH_SECTIONS,
                        lambda: rt.log_rows(self.character),
                        id="research-log-list",
                        group="research",
                    )
            yield DetailsPanel(self._RESEARCH_INFO_PLACEHOLDER, id="research-info")
            self._on_refresh(RESEARCH_SECTIONS, self._refresh_research_info)

    def _refresh_research_info(self) -> None:
        """The Research tab's details panel: the chosen goal (its stage,
        steps and odds) or season of the log, else the hint."""
        try:
            info = self.query_one("#research-info", Static)
        except NoMatches:
            return
        goals = self.character.breakthroughs
        index = self.selected_research_goal()
        if index is not None and index < len(goals):
            info.update(rt.goal_panel(self.saga, self.character, goals[index]))
            return
        entries = rt.log_entries(self.character)
        index = self.query_one("#research-log-list", SelectableList).selected_data_index
        if index is not None and index < len(entries):
            info.update(rt.attempt_panel(*entries[index]))
            return
        info.update(self._RESEARCH_INFO_PLACEHOLDER)

    def _inventory_tab(self) -> ComposeResult:
        """Raw Vis (magi), Personal Gear and the character's Books over the
        details panel of the chosen item or book."""
        character = self.character
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                if character.type == "magus":
                    with SheetSection(title="Raw Vis", id="section-raw-vis-inventory"):
                        yield self._list(
                            self._RAW_VIS_SECTIONS,
                            self._raw_vis_rows,
                            id="raw-vis-list-inventory",
                        )
                with SheetSection(
                    title=self._titled(
                        "section-inventory",
                        "section-inventory",
                        lambda: cs.gear_title(self.character),
                    ),
                    id="section-inventory",
                ):
                    yield self._list(
                        "section-inventory",
                        self._inventory_rows,
                        id="inventory-list",
                        group="char-inv",
                    )
                yield from self._devices(
                    "character", character.id, "section-char-devices", group="char-inv"
                )
                yield self._book_list(
                    ("section-char-info",),
                    lambda: library.books_owned_by(
                        self.saga, "character", character.id
                    ),
                    section_id="section-books",
                    docked=False,
                    group="char-inv",
                )
            yield DetailsPanel(self._inventory_info_text(None), id="inventory-info")
        self._on_refresh(
            (
                "section-inventory",
                "section-char-devices",
                "section-books",
                "section-char-info",
            ),
            self._refresh_inventory_info,
        )

    def _agents_tab(self) -> ComposeResult:
        """The agents he controls through personal bonds: the limit and
        the Agency experience, the list, and the chosen agent's details."""
        character = self.character
        self.core_ops[AGENTS_SECTION] = agent_forms.ops(character)
        with Vertical(classes="panel-body"):
            with (
                VerticalScroll(),
                SheetSection(
                    title=self._titled(
                        AGENTS_SECTION,
                        AGENTS_SECTION,
                        lambda: agent_forms.title(self.character),
                    ),
                    id=AGENTS_SECTION,
                ),
            ):
                yield self._static(
                    AGENTS_SOURCES,
                    lambda: agent_forms.header(self.character, two_lines=True),
                    id="char-agents-header",
                )
                yield TableHeader(agent_forms.table_header())
                yield self._list(
                    AGENTS_SECTION,
                    lambda: agent_forms.rows(self.character),
                    id=AGENTS_LIST,
                )
            yield self._panel(
                AGENTS_SOURCES,
                lambda: agent_forms.info(
                    self.character, self.section_row(AGENTS_SECTION), wide=True
                ),
                id=AGENTS_INFO,
            )

    def selected_personality_trait(self) -> int | None:
        """Index into character.personality_traits of the chosen row, or None."""
        return self.query_one(
            "#personality-traits-list", SelectableList
        ).selected_data_index

    def selected_reputation(self) -> int | None:
        """Index into character.reputations of the chosen row, or None."""
        return self.query_one(
            "#character-reputations-list", SelectableList
        ).selected_data_index

    def selected_raw_vis(self, section_id: str) -> int | None:
        """Index into sorted(character.raw_vis) of the chosen row in
        whichever of the two Raw Vis lists `section_id` (one of
        "section-raw-vis-hermetic"/"section-raw-vis-inventory") names, or
        None."""
        list_id = (
            "#raw-vis-list-hermetic"
            if section_id == "section-raw-vis-hermetic"
            else "#raw-vis-list-inventory"
        )
        return self.query_one(list_id, SelectableList).selected_data_index

    def selected_known_spell(self) -> int | None:
        """Index into character.spells_known of the chosen row, or None."""
        return self.query_one("#known-spells-list", SelectableList).selected_data_index

    def selected_inventory_item(self) -> int | None:
        """Index into character.inventory of the chosen row, or None."""
        return self.query_one("#inventory-list", SelectableList).selected_data_index

    def selected_ability(self) -> int | None:
        """Index into character.abilities of the chosen row, or None."""
        return self.query_one("#abilities-list", SelectableList).selected_data_index

    def selected_virtue_flaw(self) -> int | None:
        """Index into character.virtues_flaws of the row chosen in either
        the Virtues or the Flaws list, or None if neither has one chosen."""
        virtues = self.query_one("#vf-virtues-list", SelectableList).selected_data_index
        if virtues is not None:
            return virtues
        return self.query_one("#vf-flaws-list", SelectableList).selected_data_index

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        list_id = event.selectable_list.id or ""
        if list_id == AHEAD_LIST:
            event.stop()
            self.query_one(f"#{AHEAD_INFO}", Static).update(
                seasons.ahead_info(self.saga, self.character, event.data_index)
            )
            return
        if list_id == AGENTS_LIST:
            event.stop()
            self.query_one(f"#{AGENTS_INFO}", Static).update(
                agent_forms.info(self.character, event.data_index, wide=True)
            )
            return
        if list_id == "char-diary-list":
            event.stop()
            self.query_one("#char-diary-info", Static).update(
                lab_text.diary_info_text(self.character.diary, event.data_index)
            )
            return
        if list_id.startswith("trad-") and list_id.endswith("-list"):
            event.stop()
            self.query_one(f"#{list_id.removesuffix('-list')}-info", Static).update(
                self._ability_info_text(event.data_index)
            )
            return
        if list_id == "abilities-list":
            event.stop()
            self.query_one("#ability-info", Static).update(
                self._ability_info_text(event.data_index)
            )
            return
        if list_id in (
            "inventory-list",
            "section-char-devices-list",
            "section-books-list",
        ):
            event.stop()
            # One group (one selection across the three), one details panel.
            self._refresh_inventory_info()
            return
        if list_id in (
            "arts-techniques-list",
            "arts-forms-list",
            "known-spells-list",
        ):
            event.stop()
            # One group (one selection across the three), one details panel.
            self._refresh_hermetic_info()
            return
        if list_id in ("research-goals-list", "research-log-list"):
            event.stop()
            self._refresh_research_info()
            return
        if list_id == "char-powers-list":
            event.stop()
            self.query_one("#vf-info", Static).update(
                power_forms.info(self.character, event.data_index, self.saga)
            )
            return
        if list_id not in ("vf-virtues-list", "vf-flaws-list"):
            return
        event.stop()
        # A Virtue or Flaw row was chosen (the other list is unchosen: same
        # group): fill the details panel.
        self.query_one("#vf-info", Static).update(self._vf_info_text(event.data_index))

    def _info_left_text(self) -> str:
        return cs.info_left_text(self.saga, self.character)

    def _info_right_text(self) -> str:
        return cs.info_right_text(self.saga, self.character)

    def _biographical_left_text(self) -> str:
        return cs.biographical_left_text(self.saga, self.character)

    def _biographical_right_text(self) -> str:
        return cs.biographical_right_text(self.character)

    def _characteristics_text(self) -> str:
        return st.characteristics_text(
            self.character.characteristics, cunning=self.character.animal is not None
        )

    def _ability_rows(self) -> list[tuple[int | None, str]]:
        return st.ability_rows(
            self.character.abilities,
            self.character.virtues_flaws,
            traditions.claimed(self.character),
        )

    def _ability_info_text(self, index: int | None) -> str:
        return st.ability_info_text(
            self.character.abilities, index, self.character.virtues_flaws
        )

    def _vf_rows(self, vf_type: str) -> list[tuple[int | None, str]]:
        free = cv.free_benefit(self.character).free_indices
        return st.vf_rows(self.character.virtues_flaws, vf_type, free)

    def _vf_title(self, vf_type: str) -> str:
        """ "Virtues (3 pts)" / "Flaws (3 pts)": the points each side comes
        to, both coloured by whether they balance. A magus's free House
        Virtue (and Ex Miscellanea's compulsory Flaw) counts nothing
        (cv.HOUSE_SOURCE)."""
        vfs = self.character.virtues_flaws
        free = cv.free_benefit(self.character).free_indices
        virtues = st.vf_points(vfs, "Virtue", free)
        flaws = st.vf_points(vfs, "Flaw", free)
        return points_title(
            f"{vf_type}s",
            virtues if vf_type == "Virtue" else flaws,
            match_colour(virtues, flaws),
        )

    def _vf_info_text(self, index: int | None) -> str:
        return st.vf_info_text(self.character.virtues_flaws, index)

    def _aging_text(self) -> str:
        return cs.aging_text(self.character, self.saga)

    def _personality_trait_rows(self) -> list[tuple[int | None, str]]:
        return st.trait_rows(self.character.personality_traits)

    def _reputation_rows(self) -> list[tuple[int | None, str]]:
        return st.trait_rows(self.character.reputations)

    def _wounds_text(self) -> str:
        return st.character_wounds_text(self.character, self.saga)

    def _fatigue_text(self) -> str:
        return st.character_fatigue_text(self.character)

    def _raw_vis_rows(self) -> list[tuple[int | None, str]]:
        return cs.raw_vis_rows(self.character)

    def _hermetic_background_left_text(self) -> str:
        return cs.hermetic_background_left_text(self.character)

    def _hermetic_background_right_text(self) -> str:
        return cs.hermetic_background_right_text(self.saga, self.character)

    _ARTS_NAME_WIDTH: ClassVar[int] = 16
    _ARTS_NUM_WIDTH: ClassVar[int] = 6
    #: Wide enough for a boosted score, "10 (13)".
    _ARTS_SCORE_WIDTH: ClassVar[int] = 9

    def _arts_header_text(self) -> str:
        """Column titles above an Arts list, aligned with _art_row_label()
        (the two-character indent is the list's selector marker)."""
        return (
            f"  {'':<{self._ARTS_NAME_WIDTH}}"
            f"{'Score':>{self._ARTS_SCORE_WIDTH}}{'XP':>{self._ARTS_NUM_WIDTH}}"
        )

    def _art_row_label(self, art: str) -> str:
        row = cs.art_row(self.character, art)
        name = f"{row.art} ({row.abbreviation})"
        return (
            f"{name:<{self._ARTS_NAME_WIDTH}}"
            f"{row.score:>{self._ARTS_SCORE_WIDTH}}{row.xp:>{self._ARTS_NUM_WIDTH}}"
        )

    def _arts_rows(self, arts: Sequence[str]) -> list[tuple[int, str]]:
        return [(i, self._art_row_label(art)) for i, art in enumerate(arts)]

    def _art_info_text(self, art: str) -> str:
        return cs.art_info_text(self.character, art)

    def _refresh_hermetic_info(self) -> None:
        """The Hermetic Magic tab's single details panel, shared by the
        Magical Arts columns and Known Spells (only one of the three lists
        has a selection at a time -- see on_selectable_list_chosen())."""
        try:
            info = self.query_one("#hermetic-info", Static)
        except NoMatches:
            return
        index = self.query_one(
            "#arts-techniques-list", SelectableList
        ).selected_data_index
        if index is not None:
            info.update(self._art_info_text(TECHNIQUES[index]))
            return
        index = self.query_one("#arts-forms-list", SelectableList).selected_data_index
        if index is not None:
            info.update(self._art_info_text(FORMS[index]))
            return
        index = self.query_one("#known-spells-list", SelectableList).selected_data_index
        info.update(self._known_spell_info_text(index))

    def _research_goal_rows(self) -> list[tuple[int | None, str]]:
        return [
            (index, st.goal_row(goal))
            for index, goal in enumerate(self.character.breakthroughs)
        ]

    def selected_research_goal(self) -> int | None:
        """Index into character.breakthroughs of the chosen row, or None."""
        return self.query_one(
            "#research-goals-list", SelectableList
        ).selected_data_index

    def _known_spell_rows(self) -> list[tuple[int | None, str]]:
        return st.known_spell_rows(self.saga, self.character)

    def _known_spell_info_text(self, index: int | None) -> str:
        if index is None:  # nothing chosen in any of the panel's three lists
            return self._HERMETIC_INFO_PLACEHOLDER
        return cs.known_spell_info_text(self.saga, self.character, index)

    def _inventory_rows(self) -> list[tuple[int | None, str]]:
        return cs.inventory_rows(self.character)

    #: The Inventory tab's details panel with nothing chosen.
    _INVENTORY_HINT = (
        "[dim]Select an item, an enchanted device or a book to see its details.[/]"
    )

    def _inventory_info_text(self, index: int | None) -> str:
        if index is None:
            return self._INVENTORY_HINT
        return cs.inventory_item_text(self.character, index)

    def _refresh_inventory_info(self) -> None:
        """The Inventory tab's details panel: the chosen item, enchanted
        device or book (one selection across the three lists), else the
        hint."""
        info = self.query_one("#inventory-info", Static)
        index = self.query_one("#inventory-list", SelectableList).selected_data_index
        if index is not None and index < len(self.character.inventory):
            info.update(self._inventory_info_text(index))
            return
        device = self.selected_device_row("section-char-devices")
        if device is not None:
            info.update(
                self._device_panel_text(
                    "character", self.character.id, device, self._INVENTORY_HINT
                )
            )
            return
        book = self.query_one(BookListView).selected_book()
        if book is not None and lt.is_lab_text(book):
            # A Lab Text shows how it stands for this character.
            info.update(lt.detail_text(self.saga, self.character, book))
            return
        info.update(
            bk.detail_text(self.saga, book)
            if book is not None
            else self._inventory_info_text(None)
        )
