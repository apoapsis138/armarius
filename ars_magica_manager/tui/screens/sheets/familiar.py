"""The Familiar sheet."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import (
    Button,
    Static,
    TabbedContent,
)

from .... import familiars as fam
from .... import possessions as pos
from .... import sheet_text as st
from ....models import (
    Familiar,
    Saga,
)
from ..widgets import (
    PinnedCollapsible,
    SelectableList,
    SheetSection,
    TableHeader,
    TwoColumns,
    counted,
    points_title,
)
from .base import SheetView


class FamiliarSheetView(SheetView):
    """The Familiar sheet mounted into WorkspaceScreen's detail pane.

    A fixed top panel (Familiar Info -- not inside any tab, permanently
    expanded, same PinnedCollapsible pattern as the other sheets) above a
    5-tab body mirroring reference/familiar-rules-and-sheet.md: Identity &
    Cords (Binding & Cords, Virtues & Flaws, Personality Traits &
    Reputations), Characteristics (the 8 Characteristics plus the typed-in
    Base Soak/Magic Resistance figures) and Combat & Health (Wounds/Fatigue,
    reusing Character's own dialogs; Natural Weapons & Attacks, a free
    selectable list of weapon-kind Possessions -- same shape as Character's
    weapon rows), Abilities and Bond Powers.
    """

    DEFAULT_CSS = """
    FamiliarSheetView #fam-top-panel {
        width: 1fr;
        height: auto;
    }
    """

    def __init__(self, saga: Saga, familiar: Familiar) -> None:
        super().__init__(saga)
        self.familiar = familiar

    INITIAL_TAB = "tab-fam-identity"

    def compose(self) -> ComposeResult:
        with (
            Vertical(id="fam-top-panel"),
            PinnedCollapsible(title="Familiar Info", id="section-fam-info"),
        ):
            yield self._static(
                "section-fam-info",
                lambda: fam.identity_text(self.saga, self.familiar),
                id="fam-info-content",
            )
            yield Button("Edit (e)", id="btn-fam-info-edit", compact=True)
        with TabbedContent(initial=self.INITIAL_TAB):
            yield self._tab("Identity & Cords", "tab-fam-identity", self._identity_tab)
            yield self._tab(
                "Characteristics",
                "tab-fam-characteristics",
                self._characteristics_tab,
            )
            yield self._tab("Combat & Health", "tab-fam-combat", self._combat_tab)
            yield self._tab("Abilities", "tab-fam-abilities", self._abilities_tab)
            yield self._tab("Bond Powers", "tab-fam-powers", self._powers_tab)

    def _characteristics_tab(self) -> ComposeResult:
        with SheetSection(title="Characteristics", id="section-fam-characteristics"):
            yield self._static(
                "section-fam-characteristics",
                lambda: fam.characteristics_text(self.familiar),
                id="fam-characteristics-content",
            )

    def _abilities_tab(self) -> ComposeResult:
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                yield Static(
                    "[dim]Languages: shares the Magus partner's Language "
                    "scores automatically.[/]"
                )
                yield self._list(
                    "tab-fam-abilities",
                    lambda: fam.ability_rows(self.familiar),
                    id="fam-abilities-list",
                )
            yield self._panel(
                "tab-fam-abilities",
                lambda: fam.ability_info_text(self.familiar, None),
                id="fam-ability-info",
            )

    def _powers_tab(self) -> ComposeResult:
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                yield self._list(
                    "tab-fam-powers",
                    lambda: fam.bond_power_rows(self.familiar),
                    id="fam-bond-powers-list",
                )
            yield self._panel(
                "tab-fam-powers",
                lambda: fam.bond_power_info_text(self.familiar, None),
                id="fam-bond-powers-info",
            )

    def _identity_tab(self) -> ComposeResult:
        """Binding & Cords, the Virtue and Flaw lists with their details
        panel, and Personality Traits and Reputations."""
        vf_sections = ("section-fam-vf-virtues", "section-fam-vf-flaws")
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                with SheetSection(title="Binding & Cords", id="section-fam-binding"):
                    yield self._static(
                        "section-fam-binding",
                        self._binding_text,
                        id="fam-binding-content",
                    )
                with TwoColumns(id="fam-vf-row"):
                    with SheetSection(
                        title=self._titled(
                            vf_sections,
                            "section-fam-vf-virtues",
                            lambda: points_title(
                                "Virtues",
                                st.vf_points(self.familiar.virtues_flaws, "Virtue"),
                            ),
                        ),
                        id="section-fam-vf-virtues",
                    ):
                        yield self._list(
                            vf_sections,
                            lambda: fam.vf_rows(self.familiar, "Virtue"),
                            id="fam-vf-virtues-list",
                            group="fam-vf",
                        )
                    with SheetSection(
                        title=self._titled(
                            vf_sections,
                            "section-fam-vf-flaws",
                            lambda: points_title(
                                "Flaws",
                                st.vf_points(self.familiar.virtues_flaws, "Flaw"),
                            ),
                        ),
                        id="section-fam-vf-flaws",
                    ):
                        yield self._list(
                            vf_sections,
                            lambda: fam.vf_rows(self.familiar, "Flaw"),
                            id="fam-vf-flaws-list",
                            group="fam-vf",
                        )
                with TwoColumns(id="fam-pt-rep-row"):
                    with SheetSection(
                        title=self._titled(
                            "section-fam-personality-traits",
                            "section-fam-personality-traits",
                            lambda: counted(
                                "Personality Traits",
                                len(self.familiar.personality_traits),
                            ),
                        ),
                        id="section-fam-personality-traits",
                    ):
                        yield self._list(
                            "section-fam-personality-traits",
                            lambda: fam.personality_trait_rows(self.familiar),
                            id="fam-personality-traits-list",
                        )
                    with SheetSection(
                        title=self._titled(
                            "section-fam-reputations",
                            "section-fam-reputations",
                            lambda: counted(
                                "Reputations", len(self.familiar.reputations)
                            ),
                        ),
                        id="section-fam-reputations",
                    ):
                        yield self._list(
                            "section-fam-reputations",
                            lambda: fam.reputation_rows(self.familiar),
                            id="fam-reputations-list",
                        )
            yield self._panel(
                vf_sections,
                lambda: fam.vf_info_text(self.familiar, None),
                id="fam-vf-info",
            )

    def _combat_tab(self) -> ComposeResult:
        """Health (Wounds and Fatigue) and Natural Weapons & Attacks, over
        the details panel of the chosen weapon."""
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                with (
                    SheetSection(title="Health", id="section-fam-health"),
                    TwoColumns(id="fam-health-row", text=True),
                ):
                    with Vertical(id="fam-health-wounds-col"):
                        yield self._static(
                            "section-fam-health",
                            lambda: fam.wounds_text(self.familiar),
                            id="fam-wounds-content",
                        )
                        yield Button(
                            "Edit Wounds (e)",
                            id="btn-fam-health-wounds-edit",
                            compact=True,
                        )
                    with Vertical(id="fam-health-fatigue-col"):
                        yield self._static(
                            "section-fam-health",
                            lambda: fam.fatigue_text(self.familiar),
                            id="fam-fatigue-content",
                        )
                        yield Button(
                            "Edit Fatigue",
                            id="btn-fam-health-fatigue-edit",
                            compact=True,
                        )
                with SheetSection(
                    title=self._titled(
                        "section-fam-natural-weapons",
                        "section-fam-natural-weapons",
                        lambda: counted(
                            "Natural Weapons & Attacks",
                            len(self.familiar.natural_weapons),
                        ),
                    ),
                    id="section-fam-natural-weapons",
                ):
                    yield TableHeader(pos.table_header("weapon"))
                    yield self._list(
                        "section-fam-natural-weapons",
                        lambda: fam.natural_weapon_rows(self.familiar),
                        id="fam-natural-weapons-list",
                    )
            yield self._panel(
                "section-fam-natural-weapons",
                lambda: fam.natural_weapon_info_text(self.familiar, None),
                id="fam-natural-weapons-info",
            )

    def _binding_text(self) -> str:
        return f"{fam.binding_text(self.familiar)}\n\n{fam.cords_text(self.familiar)}"

    def selected_virtue_flaw(self) -> int | None:
        """Index into familiar.virtues_flaws of the row chosen in either the
        Virtues or the Flaws list, or None if neither has one chosen."""
        virtues = self.query_one(
            "#fam-vf-virtues-list", SelectableList
        ).selected_data_index
        if virtues is not None:
            return virtues
        return self.query_one("#fam-vf-flaws-list", SelectableList).selected_data_index

    def selected_personality_trait(self) -> int | None:
        return self.query_one(
            "#fam-personality-traits-list", SelectableList
        ).selected_data_index

    def selected_reputation(self) -> int | None:
        return self.query_one(
            "#fam-reputations-list", SelectableList
        ).selected_data_index

    def selected_natural_weapon(self) -> int | None:
        return self.query_one(
            "#fam-natural-weapons-list", SelectableList
        ).selected_data_index

    def selected_ability(self) -> int | None:
        return self.query_one("#fam-abilities-list", SelectableList).selected_data_index

    def selected_bond_power(self) -> int | None:
        return self.query_one(
            "#fam-bond-powers-list", SelectableList
        ).selected_data_index

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        list_id = event.selectable_list.id or ""
        if list_id == "fam-natural-weapons-list":
            event.stop()
            self.query_one("#fam-natural-weapons-info", Static).update(
                fam.natural_weapon_info_text(self.familiar, event.data_index)
            )
            return
        if list_id == "fam-abilities-list":
            event.stop()
            self.query_one("#fam-ability-info", Static).update(
                fam.ability_info_text(self.familiar, event.data_index)
            )
            return
        if list_id == "fam-bond-powers-list":
            event.stop()
            self.query_one("#fam-bond-powers-info", Static).update(
                fam.bond_power_info_text(self.familiar, event.data_index)
            )
            return
        if list_id not in ("fam-vf-virtues-list", "fam-vf-flaws-list"):
            return
        event.stop()
        self.query_one("#fam-vf-info", Static).update(
            fam.vf_info_text(self.familiar, event.data_index)
        )
