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

from ... import books as bk
from ... import casting_text, catalog, faith, seasons
from ... import enchanted_devices as ed
from ... import lab_texts as lt
from ... import laboratories as lab_text
from ... import players as pl
from ... import possessions as pos
from ... import sheet_text as st
from ... import spells as spl
from ...arts import ART_ABBREVIATIONS, ART_DESCRIPTIONS, FORMS, TECHNIQUES
from ...markup import aligned, escape, problem
from ...models import (
    ArtScore,
    Character,
    Saga,
    character_age,
)
from ...rules import creation_virtues as cv
from ...rules import scores
from ..widgets import (
    DetailsPanel,
    PinnedCollapsible,
    SelectableList,
    SheetSection,
    TableHeader,
    TwoColumns,
    counted,
    match_colour,
    points_title,
)
from .base import SheetView
from .lists import BookListView


class CharacterSheetView(SheetView):
    """The character sheet mounted into WorkspaceScreen's detail pane.

    A fixed top panel (Info above Characteristics -- not inside any tab,
    permanently expanded, same PinnedCollapsible pattern as
    CovenantSheetView/LaboratorySheetView) above the tabbed body. Tab
    order: Description, Abilities,
    Virtues & Flaws, Hermetic Magic (magi only), Inventory, Planning, Diary.
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
    - Inventory (tab, id "tab-inventory"): Raw Vis (magi only, the second
      of the two duplicated instances -- see Hermetic Magic above),
      Personal Gear (renamed from "Inventory", same character.inventory
      data), Books.
    - Planning (tab, id "tab-planning", every character type): This Season,
      the season's plan and what it will give; a grog's
      says grogs are updated yearly.
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

    @property
    def creation_record(self) -> Character:
        return self.character

    INITIAL_TAB = "tab-description"

    def compose(self) -> ComposeResult:
        character = self.character
        yield from self._top_panel()
        with TabbedContent(initial=self.INITIAL_TAB):
            yield self._tab("Description", "tab-description", self._description_tab)
            yield self._tab("Abilities", "tab-abilities", self._abilities_tab)
            yield self._tab("Virtues & Flaws", "tab-vf", self._virtues_flaws_tab)
            if character.type == "magus":
                yield self._tab("Hermetic Magic", "tab-hermetic", self._hermetic_tab)
            yield self._tab("Inventory", "tab-inventory", self._inventory_tab)
            yield self._tab(
                "Planning", "tab-planning", self._scrolling(self._planning_tab)
            )
            yield self._tab("Diary", "tab-diary", self._diary_tab)

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
        """This Season: the season's plan and what it will give."""
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
                "section-char-season",
                lambda: seasons.plan_text(self.saga, self.character),
                id="char-season-content",
            )

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
        Traits and Reputations, Aging & Warping, and Health."""
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
            with SheetSection(title="Aging & Warping", id="section-aging"):
                yield self._static(
                    "section-aging", self._aging_text, id="aging-content"
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
            with VerticalScroll(), TwoColumns(id="vf-row"):
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
                        vf_sections, "section-vf-flaws", lambda: self._vf_title("Flaw")
                    ),
                    id="section-vf-flaws",
                ):
                    yield self._list(
                        vf_sections,
                        lambda: self._vf_rows("Flaw"),
                        id="vf-flaws-list",
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
        "[dim]Select an Art, a Known Spell or a Research Goal to see its details.[/]"
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
                        group="hermetic",
                    )
            yield DetailsPanel(self._HERMETIC_INFO_PLACEHOLDER, id="hermetic-info")
            self._on_refresh(
                ("section-arts", "section-known-spells", "section-research-goals"),
                self._refresh_hermetic_info,
            )

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
                        lambda: counted("Personal Gear", len(self.character.inventory)),
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
                    lambda: bk.books_owned_by(self.saga, "character", character.id),
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
        if list_id == "char-diary-list":
            event.stop()
            self.query_one("#char-diary-info", Static).update(
                lab_text.diary_info_text(self.character.diary, event.data_index)
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
            "research-goals-list",
        ):
            event.stop()
            # One group (one selection across the four), one details panel.
            self._refresh_hermetic_info()
            return
        if list_id not in ("vf-virtues-list", "vf-flaws-list"):
            return
        event.stop()
        # A Virtue or Flaw row was chosen (the other list is unchosen: same
        # group): fill the details panel.
        self.query_one("#vf-info", Static).update(self._vf_info_text(event.data_index))

    def _info_left_text(self) -> str:
        b = self.character.background
        age = character_age(b.year_born, self.saga.current_year)
        return aligned(
            [
                ("Setting", b.setting or "(not set)"),
                (
                    "Age",
                    age if age is not None else "(unknown -- set Year Born)",
                ),
                ("Current Year", self._inherited(str(self.saga.current_year))),
                ("Current Season", self._inherited(self.saga.current_season)),
            ]
        )

    def _info_right_text(self) -> str:
        saga, character = self.saga, self.character
        covenant = saga.covenant(character.covenant_id)
        rows = [("Covenant", escape(covenant.name) if covenant else "(unassigned)")]
        if character.type == "magus":
            lab = saga.laboratory(character.assigned_lab_id)
            rows.append(
                ("Assigned Laboratory", escape(lab.name) if lab else "(unassigned)")
            )
        b = character.background
        rows += [
            ("Type", character.type),
            ("Confidence Score", str(b.confidence_score)),
            ("Confidence Points", str(b.confidence_points)),
        ]
        if faith.shows_faith(character):
            rows += [
                ("True Faith Score", st.faith_score_text(character)),
                ("Faith Points", str(b.faith_points)),
            ]
        rows.append(("Size", st.size_text(character)))
        return aligned(rows)

    def _biographical_left_text(self) -> str:
        """Column 1 of Biographical Detail: every field except Biography
        (column 2, see _biographical_right_text()) -- the remaining
        Background fields (Setting/Confidence/Size live in the top panel)
        plus every Description field but the free-text Biography box."""
        b, d = self.character.background, self.character.description
        played_by = []
        if self.saga.players:  # a hosted saga's sign-in
            player = pl.player_by_id(self.saga, b.player_id)
            played_by = [f"Played by: {escape(player.name) if player else '(no one)'}"]
        return "\n".join(
            [
                f"Player: {escape(b.player) or '(not set)'}",
                *played_by,
                f"Birth Name: {escape(b.birth_name) or '(not set)'}",
                f"Year Born: {b.year_born if b.year_born is not None else '(not set)'}",
                f"Race/Nationality: {escape(b.race_nationality) or '(not set)'}",
                f"Place of Origin: {escape(b.place_of_origin) or '(not set)'}",
                f"Religion: {escape(b.religion) or '(not set)'}",
                f"Title/Profession: {escape(b.title_profession) or '(not set)'}",
                f"Height: {d.height if d.height is not None else '(not set)'}",
                f"Weight: {d.weight if d.weight is not None else '(not set)'}",
                f"Hair: {escape(d.hair) or '(not set)'}",
                f"Eyes: {escape(d.eyes) or '(not set)'}",
                f"Handedness: {d.handedness}",
                f"Physical Description: "
                f"{escape(d.physical_description) or '(not set)'}",
            ]
        )

    def _biographical_right_text(self) -> str:
        """Column 2 of Biographical Detail: just the free-text Biography
        box (distinct from Physical Description -- see Description's
        docstring in models/character.py)."""
        return escape(self.character.description.biography) or "(none recorded)"

    def _characteristics_text(self) -> str:
        return st.characteristics_text(self.character.characteristics)

    def _ability_rows(self) -> list[tuple[int | None, str]]:
        return st.ability_rows(self.character.abilities, self.character.virtues_flaws)

    def _ability_info_text(self, index: int | None) -> str:
        return st.ability_info_text(
            self.character.abilities, index, self.character.virtues_flaws
        )

    def _vf_rows(self, vf_type: str) -> list[tuple[int | None, str]]:
        free = cv.house_benefit(self.character).free_indices
        return st.vf_rows(self.character.virtues_flaws, vf_type, free)

    def _vf_title(self, vf_type: str) -> str:
        """ "Virtues (3 pts)" / "Flaws (3 pts)": the points each side comes
        to, both coloured by whether they balance. A magus's free House
        Virtue (and Ex Miscellanea's compulsory Flaw) counts nothing
        (cv.HOUSE_SOURCE)."""
        vfs = self.character.virtues_flaws
        free = cv.house_benefit(self.character).free_indices
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
        a = self.character.aging
        lines = [f"Decrepitude: {a.decrepitude}"]
        # The yearly aging roll's figures, once there are any.
        if a.decrepitude_points:
            lines[0] += f" ({a.decrepitude_points} points)"
        if a.apparent_age is not None:
            lines.append(f"Apparent age: {a.apparent_age}")
        points = [f"{n.title()} {p}" for n, p in a.aging_points.items() if p]
        if points:
            lines.append("Aging Points: " + ", ".join(points))
        if a.longevity_modifier:
            lines.append(f"Longevity Ritual: -{a.longevity_modifier} to aging rolls")
        if a.recovering:
            lines.append(f"Recovering from an Aging Crisis: {a.recovering}")
        return "\n".join(
            [
                *lines,
                "Effects of Aging:",
                escape(a.effects) or "(none recorded)",
                "",
                f"Warping: {a.warping_score}/{a.warping_points}",
            ]
        )

    def _personality_trait_rows(self) -> list[tuple[int | None, str]]:
        return st.trait_rows(self.character.personality_traits)

    def _reputation_rows(self) -> list[tuple[int | None, str]]:
        return st.trait_rows(self.character.reputations)

    def _wounds_text(self) -> str:
        return st.character_wounds_text(self.character)

    def _fatigue_text(self) -> str:
        return st.character_fatigue_text(self.character)

    def _raw_vis_rows(self) -> list[tuple[int | None, str]]:
        return [
            (index, f"{art.title()}: {self.character.raw_vis[art]} pawn(s)")
            for index, art in enumerate(sorted(self.character.raw_vis))
        ]

    def _hermetic_background_left_text(self) -> str:
        """Column 1 of Hermetic Background: everything but Wizard's Sigil
        (column 2, see _hermetic_background_right_text())."""
        h = self.character.hermetic
        house_catalog = catalog.load_house_catalog_by_id()
        house = house_catalog.get(h.house) if h.house else None
        return "\n".join(
            [
                f"House: {escape(house.name) if house else '(not set)'}",
                f"Domus Magna: {escape(h.domus_magna) or '(not set)'}",
                f"Primus: {escape(h.primus) or '(not set)'}",
                f"Parens: {escape(h.parens) or '(not set)'}",
                f"Covenant of Apprenticeship: "
                f"{escape(h.covenant_of_apprenticeship) or '(not set)'}",
                f"Age of Apprenticeship: "
                f"{h.age_of_apprenticeship if h.age_of_apprenticeship is not None else '(not set)'}",
            ]
        )

    def _hermetic_background_right_text(self) -> str:
        """Column 2 of Hermetic Background: Wizard's Sigil, and whose raw
        Lab Texts the magus reads."""
        sigil = self.character.hermetic.wizards_sigil
        return (
            f"Wizard's Sigil: {escape(sigil) or '(not set)'}\n"
            f"{lt.access_text(self.saga, self.character)}"
        )

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
        score = self.character.arts.get(art.lower(), ArtScore())
        bonus, _ = scores.art_bonus(self.character.virtues_flaws, art)
        shown = st.adjusted_score(score.level, bonus)
        name = f"{art} ({ART_ABBREVIATIONS[art]})"
        return (
            f"{name:<{self._ARTS_NAME_WIDTH}}"
            f"{shown:>{self._ARTS_SCORE_WIDTH}}{score.xp:>{self._ARTS_NUM_WIDTH}}"
        )

    def _arts_rows(self, arts: Sequence[str]) -> list[tuple[int, str]]:
        return [(i, self._art_row_label(art)) for i, art in enumerate(arts)]

    def _art_info_text(self, art: str) -> str:
        score = self.character.arts.get(art.lower(), ArtScore())
        bonus, bonus_from = scores.art_bonus(self.character.virtues_flaws, art)
        return "\n".join(
            [
                f"[b]Name:[/] {art} ({ART_ABBREVIATIONS[art]})",
                st.xp_line(score.progress, bonus, bonus_from),
                "",
                f"[b]Description:[/] {ART_DESCRIPTIONS[art]}",
            ]
        )

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
        index = self.query_one(
            "#research-goals-list", SelectableList
        ).selected_data_index
        if index is not None and index < len(self.character.breakthroughs):
            info.update(st.goal_text(self.character.breakthroughs[index]))
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
        known = self.character.spells_known[index]
        spell = spl.find_spell(self.saga, known.spell_id)
        if spell is None:
            lines = [problem(f"Unknown spell: {escape(known.spell_id)}")]
        else:
            lines = [spl.detail_text(self.saga, spell), ""]
            lines += casting_text.known_spell_casting_lines(
                self.saga, self.character, known, spell
            )
        lines += [
            "",
            "[b]Mastery:[/]",
            f"Score {known.mastery_score}, XP {known.mastery_xp}",
        ]
        if known.mastery_abilities:
            for ability in known.mastery_abilities:
                lines.append(f"  {escape(ability.name)} {ability.level}/{ability.xp}")
        else:
            lines.append("  (no Mastery Abilities)")
        return "\n".join(lines)

    #: Character Inventory's group headers, in display order.
    _INVENTORY_KINDS: ClassVar[tuple[str, ...]] = ("weapon", "armor", "item")
    _INVENTORY_HEADERS: ClassVar[dict[str, str]] = {
        "weapon": "Weapons",
        "armor": "Armor",
        "item": "Other Items",
    }

    def _inventory_rows(self) -> list[tuple[int | None, str]]:
        """One selectable list for all of Inventory, with a header row --
        its title and column titles -- before each non-empty kind (Weapons,
        Armor, Other Items)."""
        rows: list[tuple[int | None, str]] = []
        for kind in self._INVENTORY_KINDS:
            indexed = [
                (i, item)
                for i, item in enumerate(self.character.inventory)
                if item.kind == kind
            ]
            if not indexed:
                continue
            rows.append((None, pos.group_header(kind, self._INVENTORY_HEADERS[kind])))
            for index, item in indexed:
                rows.append((index, pos.row_label(pos.PossessionEntry(kind, item))))
        return rows

    #: The Inventory tab's details panel with nothing chosen.
    _INVENTORY_HINT = (
        "[dim]Select an item, an enchanted device or a book to see its details.[/]"
    )

    def _inventory_info_text(self, index: int | None) -> str:
        if index is None:
            return self._INVENTORY_HINT
        item = self.character.inventory[index]
        text = pos.detail_text(pos.PossessionEntry(item.kind, item))
        if item.kind == "weapon":
            text += "\n\n" + st.combat_text(self.character, item)
        return text

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
