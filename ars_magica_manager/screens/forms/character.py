"""A character's forms: Characteristics, details, biography, aging, wounds,
fatigue, Hermetic background, familiar details and bond powers, and the
Arts and familiar binding editors."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Label, Select, Static

from ... import catalog, faith
from ... import familiars as fam
from ... import sheet_text as st
from ...arts import ART_ABBREVIATIONS, ARTS, FORMS, TECHNIQUES
from ...markup import escape, problem
from ...models import (
    COMPANION_TYPES,
    CORD_SCORE_COSTS,
    FATIGUE_LEVELS,
    SEASONS,
    Aging,
    ArtScore,
    Background,
    BondPower,
    Character,
    Characteristics,
    Description,
    Familiar,
    HermeticBackground,
    Player,
    Saga,
    VirtueFlawInstance,
    Wounds,
)
from ...rules import creation_characteristics, scores
from ...rules import xp as xp_rules
from ..fields import (
    _EMPHASIS_HINT,
    DialogField,
    FieldsDialog,
    ModalDialog,
    _attr,
    _covenant_options,
    _pairs,
    _year_born_field,
)
from .creation import _CHARACTER_TYPES

#: The eight Characteristics as (label, attribute), in the book's order.
_CHARACTERISTIC_FIELDS: list[tuple[str, str]] = [
    ("Intelligence (Int)", "intelligence"),
    ("Perception (Per)", "perception"),
    ("Presence (Pre)", "presence"),
    ("Communication (Com)", "communication"),
    ("Strength (Str)", "strength"),
    ("Stamina (Sta)", "stamina"),
    ("Dexterity (Dex)", "dexterity"),
    ("Quickness (Qik)", "quickness"),
]


def _characteristics_fields(characteristics: Characteristics) -> list[DialogField]:
    return [
        DialogField(attribute, label, "int", getattr(characteristics, attribute))
        for label, attribute in _CHARACTERISTIC_FIELDS
    ]


def _characteristics_dialog(
    saga: Saga, character: Character
) -> FieldsDialog[dict[str, Any]]:
    """Edit Characteristics. While the character is In Creation the form
    shows the points spent and left as each score is typed."""
    return FieldsDialog(
        "Edit Characteristics",
        _characteristics_fields(character.characteristics),
        live=(
            (
                lambda values: creation_characteristics.points_text(
                    saga, character, values
                )
            )
            if character.in_creation
            else None
        ),
    )


def _characteristics_from(values: dict[str, Any]) -> Characteristics:
    return Characteristics(
        **{attribute: values[attribute] for _, attribute in _CHARACTERISTIC_FIELDS}
    )


def _character_info_fields(saga: Saga, character: Character) -> list[DialogField]:
    """The top panel's Edit form: name, a companion's type (Companion or
    Mythic Companion), covenant, a magus's laboratory, and the Background
    figures shown there."""
    b = character.background
    fields = [
        DialogField("name", "Name", "text", character.name, required=True),
    ]
    if character.type in COMPANION_TYPES:
        fields.append(
            DialogField(
                "type",
                "Type",
                "select",
                character.type,
                options=[t for t in _CHARACTER_TYPES if t[1] in COMPANION_TYPES],
            )
        )
    fields += [
        DialogField(
            "covenant_id",
            "Covenant",
            "select",
            character.covenant_id,
            options=_covenant_options(saga),
            allow_blank=True,
            placeholder="(unassigned)",
        ),
    ]
    if character.type == "magus":
        fields.append(
            DialogField(
                "laboratory_id",
                "Assigned Laboratory",
                "select",
                character.assigned_lab_id,
                options=[(escape(lab.name), lab.id) for lab in saga.laboratories],
                allow_blank=True,
                placeholder="(unassigned)",
            )
        )
    return fields + [
        DialogField("setting", "Setting", "text", b.setting),
        DialogField("confidence_score", "Confidence Score", "int", b.confidence_score),
        DialogField(
            "confidence_points", "Confidence Points", "int", b.confidence_points
        ),
        DialogField(
            "true_faith_score",
            "True Faith Score",
            "int",
            b.true_faith_score,
            hint="Only with the True Faith Virtue; 2+ is a Mythic Companion.",
        ),
        DialogField("faith_points", "Faith Points", "int", b.faith_points),
        DialogField("size", "Size", "int", b.size),
    ]


def _character_info_dialog(saga: Saga, character: Character) -> FieldsDialog:
    """Edit Character Info, warning (not refusing) as the True Faith Score
    is typed if the character can't have it (faith.faith_warnings)."""

    def live(values: dict[str, Any]) -> str:
        score = values.get("true_faith_score") or 0
        kind = values.get("type") or character.type
        warnings = faith.faith_warnings(character, score, kind)
        return "\n".join(problem(escape(w)) for w in warnings)

    return FieldsDialog(
        "Edit Character Info", _character_info_fields(saga, character), live=live
    )


_HANDEDNESS_OPTIONS: list[tuple[str, str]] = [
    ("Right", "right"),
    ("Left", "left"),
    ("Ambidextrous", "ambidextrous"),
]


#: Biographical Detail's free-text Background fields, as (label, attribute).
_BIOGRAPHY_TEXT_FIELDS: list[tuple[str, str]] = [
    ("Player", "player"),
    ("Birth Name", "birth_name"),
]


_BIOGRAPHY_TEXT_FIELDS_AFTER_YEAR: list[tuple[str, str]] = [
    ("Race/Nationality", "race_nationality"),
    ("Place of Origin", "place_of_origin"),
    ("Religion", "religion"),
    ("Title/Profession", "title_profession"),
]


def _played_by_field(
    background: Background, players: Sequence[Player], may_assign: bool
) -> list[DialogField]:
    """Who plays the character, from the saga's players: only
    when the saga has players, and only the storyguide may change it."""
    if not players:
        return []
    if not may_assign:
        playing = next((p for p in players if p.id == background.player_id), None)
        return [
            DialogField(
                "_played_by",
                "Played by",
                "info",
                playing.name if playing else "(no one)",
            )
        ]
    return [
        DialogField(
            "player_id",
            "Played by",
            "select",
            background.player_id,
            options=[(escape(p.name), p.id) for p in players],
            allow_blank=True,
            placeholder="(no one)",
            hint="The player who may change this character when they sign in.",
        )
    ]


def _biographical_fields(
    background: Background,
    description: Description,
    players: Sequence[Player] = (),
    *,
    may_assign: bool = True,
) -> list[DialogField]:
    """The Background fields not in the top panel, then every Description
    field."""
    d = description
    return [
        *(
            DialogField(attribute, label, "text", getattr(background, attribute))
            for label, attribute in _BIOGRAPHY_TEXT_FIELDS
        ),
        *_played_by_field(background, players, may_assign),
        _year_born_field(background.year_born),
        *(
            DialogField(attribute, label, "text", getattr(background, attribute))
            for label, attribute in _BIOGRAPHY_TEXT_FIELDS_AFTER_YEAR
        ),
        DialogField("height", "Height", "optfloat", d.height),
        DialogField("weight", "Weight", "optfloat", d.weight),
        DialogField("hair", "Hair", "text", d.hair),
        DialogField("eyes", "Eyes", "text", d.eyes),
        DialogField(
            "handedness",
            "Handedness",
            "select",
            d.handedness,
            options=_HANDEDNESS_OPTIONS,
        ),
        DialogField(
            "physical_description",
            "Physical Description",
            "text",
            d.physical_description,
        ),
        DialogField("biography", "Biography", "area", d.biography, hint=_EMPHASIS_HINT),
    ]


def _aging_fields(aging: Aging) -> list[DialogField]:
    return [
        DialogField("decrepitude", "Decrepitude", "int", aging.decrepitude),
        DialogField("effects", "Effects of Aging", "text", aging.effects),
        DialogField("warping_score", "Warping Score", "int", aging.warping_score),
        DialogField("warping_points", "Warping Points", "int", aging.warping_points),
        DialogField(
            "gain_warping",
            "Gain Warping Points now",
            "int",
            0,
            hint="From one event (a powerful effect, a botch...): 2 or more "
            "take a magus to the edge of Wizard's Twilight, rolled at once.",
        ),
    ]


def _wounds_fields(wounds: Wounds, *, soak: bool = True) -> list[DialogField]:
    """Wound counts and Incapacitated/Dead; a character's Soak too (a
    Familiar's lives with its Characteristics instead)."""
    fields = (
        [
            DialogField(
                "soak",
                "Soak adjustment",
                "int",
                wounds.soak,
                hint="Added to the Soak worked out from Stamina, armour and Virtues.",
            )
        ]
        if soak
        else []
    )
    return fields + [
        DialogField("light", "Light Wounds (-1 each)", "int", wounds.light),
        DialogField("medium", "Medium Wounds (-3 each)", "int", wounds.medium),
        DialogField("heavy", "Heavy Wounds (-5 each)", "int", wounds.heavy),
        DialogField("incapacitated", "Incapacitated", "check", wounds.incapacitated),
        DialogField("dead", "Dead", "check", wounds.dead),
    ]


def _fatigue_fields(level: str) -> list[DialogField]:
    return [
        DialogField(
            "level",
            "Level",
            "select",
            level,
            options=[(level.title(), level) for level in FATIGUE_LEVELS],
        )
    ]


def _hermetic_fields(hermetic: HermeticBackground) -> list[DialogField]:
    h = hermetic
    return [
        DialogField(
            "house",
            "House",
            "select",
            h.house,
            options=[(house.name, house.id) for house in catalog.load_house_catalog()],
            allow_blank=True,
            placeholder="(none selected)",
        ),
        DialogField("domus_magna", "Domus Magna", "text", h.domus_magna),
        DialogField("primus", "Primus", "text", h.primus),
        DialogField("parens", "Parens", "text", h.parens),
        DialogField(
            "covenant_of_apprenticeship",
            "Covenant of Apprenticeship",
            "text",
            h.covenant_of_apprenticeship,
        ),
        DialogField(
            "age_of_apprenticeship",
            "Age of Apprenticeship",
            "optint",
            h.age_of_apprenticeship,
        ),
        DialogField("wizards_sigil", "Wizard's Sigil", "area", h.wizards_sigil),
    ]


def _familiar_characteristics_fields(familiar: Familiar) -> list[DialogField]:
    return _characteristics_fields(familiar.characteristics) + [
        DialogField("base_soak", "Base Soak", "int", familiar.base_soak),
        DialogField(
            "magic_resistance", "Magic Resistance", "int", familiar.magic_resistance
        ),
    ]


def _familiar_info_fields(familiar: Familiar) -> list[DialogField]:
    f = familiar
    return [
        DialogField("name", "Name", "text", f.name, required=True),
        DialogField("species", "Species / Description", "text", f.species),
        DialogField(
            "season_bound",
            "Season Bound",
            "select",
            f.season_bound or None,
            options=_pairs(SEASONS),
            allow_blank=True,
            placeholder="(not set)",
        ),
        DialogField("year_bound", "Year Bound", "optint", f.year_bound),
        DialogField("magic_might", "Magic Might Score", "int", f.magic_might),
        DialogField("might_pool", "Current Might Pool", "optint", f.might_pool),
        DialogField("size", "Size", "int", f.size),
        DialogField("wound_multiplier", "Wound Multiplier", "int", f.wound_multiplier),
    ]


def _bond_power_fields(power: BondPower | None) -> list[DialogField]:
    """The add/edit form for one Empowered Bond Power -- all typed-in, no
    Lab Total formula computed (see BondPower's docstring)."""

    return [
        DialogField(
            "name", "Power Name", "text", _attr(power, "name", ""), required=True
        ),
        DialogField("level", "Level", "int", _attr(power, "level", 0)),
        DialogField(
            "technique",
            "Technique",
            "select",
            _attr(power, "technique", ""),
            options=_pairs(TECHNIQUES),
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField(
            "form",
            "Form",
            "select",
            _attr(power, "form", ""),
            options=_pairs(FORMS),
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField(
            "target_controller",
            "Target & Controller",
            "text",
            _attr(power, "target_controller", ""),
            placeholder="e.g. Magus (controlled by Familiar)",
        ),
        DialogField("uses_per_day", "Uses/Day", "int", _attr(power, "uses_per_day", 0)),
        DialogField(
            "penetration", "Penetration", "int", _attr(power, "penetration", 0)
        ),
        DialogField("vis_spent", "Vis Spent", "int", _attr(power, "vis_spent", 0)),
        DialogField(
            "cosmetic_trait",
            "Cosmetic Trait Manifested",
            "text",
            _attr(power, "cosmetic_trait", ""),
        ),
        DialogField(
            "instilling_progress",
            "Instilling (blank = finished)",
            "optint",
            _attr(power, "instilling_progress", None),
            hint="0 to instil it as lab work (the lab's Planning tab).",
        ),
    ]


class EditArtsScreen(ModalDialog[dict[str, ArtScore] | None]):
    """Edits all 15 Hermetic Arts at once -- a fixed grid, not an addable
    list. Two side-by-side columns (Techniques, Forms), mirroring the sheet's
    own two-column Magical Arts display -- sized to fit every row without a
    scrollbar (Forms, the taller column, is only 10 rows). Each Art's total
    XP is typed, with its score and the total xp the next score needs
    beside it in columns, updated as it changes. Dismisses with a dict of every art's lowercase name ->
    ArtScore, or None if cancelled.
    """

    DEFAULT_CSS = """
    EditArtsScreen {
        align: center middle;
    }

    #arts-dialog {
        width: auto;
        height: auto;
        max-height: 100%;
        padding: 1 2;
    }

    #arts-subtitle {
        color: $text-muted;
        margin-bottom: 1;
    }

    #arts-columns {
        width: auto;
        height: auto;
    }

    #arts-techniques-col {
        width: auto;
        height: auto;
        margin-right: 3;
    }

    #arts-forms-col {
        width: auto;
        height: auto;
    }

    .column-heading {
        text-style: bold;
    }

    /* a column's heading names the Arts' column, then the others */
    .art-head-row {
        margin-bottom: 1;
    }

    .art-row {
        width: auto;
        height: auto;
    }

    .art-row Label {
        width: 16;
        content-align: right middle;
        padding-right: 1;
    }

    /* "20 (23)  231 xp": the score, then the next score's total */
    .art-row .art-score {
        width: 18;
        content-align: left middle;
        padding-left: 1;
        color: $text-muted;
    }

    .art-row .art-head-xp {
        width: 7;
        content-align: left middle;
        padding-right: 0;
        color: $text-muted;
    }

    /* 3 digits plus the field's padding */
    .art-row Input {
        width: 7;
    }

    #arts-buttons {
        width: auto;
        height: auto;
    }

    #arts-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        arts: dict[str, ArtScore],
        virtues_flaws: Sequence[VirtueFlawInstance] = (),
    ) -> None:
        super().__init__()
        self.arts = arts
        # the owner's Puissant, for each Art's live score
        self._bonus = {
            art.lower(): scores.art_bonus(virtues_flaws, art)[0] for art in ARTS
        }

    def compose(self) -> ComposeResult:
        def row(art_name: str):
            key = art_name.lower()
            score = self.arts.get(key, ArtScore())
            yield Label(f"{art_name} ({ART_ABBREVIATIONS[art_name]})")
            yield Input(
                value=str(score.xp),
                type="integer",
                id=f"input-art-{key}-xp",
                compact=True,
            )
            yield Label(
                self._score_label(key, score.xp),
                id=f"art-score-{key}",
                classes="art-score",
            )

        def head(title: str):
            with Horizontal(classes="art-row art-head-row"):
                yield Label(title, classes="column-heading")
                yield Label("XP", classes="art-head-xp")
                yield Label(
                    f"{'Score':<{self._SCORE_WIDTH}}Next at", classes="art-score"
                )

        with Vertical(id="arts-dialog", classes="dialog-box"):
            yield Label("Edit Arts", id="arts-title", classes="dialog-title")
            yield Label(
                "Enter each Art's total XP; its score follows", id="arts-subtitle"
            )
            with Horizontal(id="arts-columns"):
                with Vertical(id="arts-techniques-col"):
                    yield from head("Techniques")
                    for technique in TECHNIQUES:
                        with Horizontal(classes="art-row"):
                            yield from row(technique)
                with Vertical(id="arts-forms-col"):
                    yield from head("Forms")
                    for form in FORMS:
                        with Horizontal(classes="art-row"):
                            yield from row(form)
            yield Static("", id="arts-error")
            with Horizontal(id="arts-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-save":
            self._try_save()

    #: The Score column's width, before Next at.
    _SCORE_WIDTH = 9

    def _score_label(self, key: str, xp: int | None) -> str:
        """The Art's score and the total xp the next score needs, "10 (13)
        66 xp" with Puissant, or "?" while the XP isn't a number."""
        if xp is None or xp < 0:
            return "?"
        progress = xp_rules.progress(xp, xp_rules.ART_FACTOR)
        score = st.adjusted_score(progress.score, self._bonus[key])
        return f"{score:<{self._SCORE_WIDTH}}{progress.next_total} xp"

    def on_input_changed(self, event: Input.Changed) -> None:
        """Keep each Art's score and next total beside its XP as the user
        types."""
        input_id = event.input.id or ""
        if not (input_id.startswith("input-art-") and input_id.endswith("-xp")):
            return
        key = input_id.removeprefix("input-art-").removesuffix("-xp")
        try:
            xp: int | None = int(event.value.strip())
        except ValueError:
            xp = None
        self.query_one(f"#art-score-{key}", Label).update(self._score_label(key, xp))

    def _try_save(self) -> None:
        error = self.query_one("#arts-error", Static)
        result: dict[str, ArtScore] = {}
        for art_name in ARTS:
            key = art_name.lower()
            xp_raw = self.query_one(f"#input-art-{key}-xp", Input).value.strip()
            try:
                xp = int(xp_raw)
            except ValueError:
                error.update(f"{art_name} needs a whole number of XP.")
                return
            if xp < 0:
                error.update(f"{art_name}'s XP can't be negative.")
                return
            result[key] = ArtScore(xp=xp)
        self.dismiss(result)


class EditFamiliarBindingScreen(ModalDialog[dict[str, object] | None]):
    """Edits a Familiar's Initial Binding details and the three Cords.
    Dismisses with a dict of field values, or None if cancelled."""

    DEFAULT_CSS = """
    EditFamiliarBindingScreen {
        align: center middle;
    }

    #fam-binding-dialog {
        width: 70;
        height: auto;
        padding: 1 2;
    }

    .fambindingedit-row {
        width: 100%;
        height: 1;
    }

    .fambindingedit-row Label {
        width: 28;
    }

    .fambindingedit-row Input, .fambindingedit-row Select {
        width: 1fr;
    }

    .fambindingedit-cost {
        width: auto;
        color: $text-muted;
        padding-left: 1;
    }

    #fam-binding-error {
        color: $error;
        height: auto;
    }

    #fam-binding-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, familiar: Familiar) -> None:
        super().__init__()
        self.familiar = familiar

    def compose(self) -> ComposeResult:
        f = self.familiar
        with Vertical(id="fam-binding-dialog", classes="dialog-box"):
            yield Label("Edit Binding & Cords")
            with Horizontal(classes="fambindingedit-row"):
                yield Label("Binding Technique")
                yield Select(
                    _pairs(TECHNIQUES),
                    value=f.binding_technique or Select.NULL,
                    allow_blank=True,
                    prompt="(not set)",
                    id="select-fam-technique",
                    compact=True,
                )
            with Horizontal(classes="fambindingedit-row"):
                yield Label("Binding Form")
                yield Select(
                    _pairs(FORMS),
                    value=f.binding_form or Select.NULL,
                    allow_blank=True,
                    prompt="(not set)",
                    id="select-fam-form",
                    compact=True,
                )
            with Horizontal(classes="fambindingedit-row"):
                yield Label("Initial Binding Lab Total")
                yield Input(
                    value=str(f.binding_lab_total),
                    type="integer",
                    id="input-fam-lab-total",
                    compact=True,
                )
            with Horizontal(classes="fambindingedit-row"):
                yield Label("Target Binding Level")
                yield Input(
                    value=str(f.target_binding_level),
                    type="integer",
                    id="input-fam-target-level",
                    compact=True,
                )
            with Horizontal(classes="fambindingedit-row"):
                yield Label("Cumulative Vis Spent (pawns)")
                yield Input(
                    value=str(f.vis_spent_binding),
                    type="integer",
                    id="input-fam-vis-spent",
                    compact=True,
                )
            for attribute, label, _blurb in fam.CORDS:
                with Horizontal(classes="fambindingedit-row"):
                    yield Label(label)
                    yield Select(
                        [(f"+{score}", score) for score in CORD_SCORE_COSTS],
                        value=getattr(f, attribute),
                        allow_blank=False,
                        id=f"select-fam-{attribute}",
                        compact=True,
                    )
                    yield Static(
                        f"{fam.cord_cost(getattr(f, attribute))} pts",
                        id=f"cost-fam-{attribute}",
                        classes="fambindingedit-cost",
                    )
            yield Static("", id="fam-binding-error")
            with Horizontal(id="fam-binding-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-save":
            self._try_save()

    def on_select_changed(self, event: Select.Changed) -> None:
        select_id = event.select.id or ""
        if not select_id.startswith("select-fam-"):
            return
        attribute = select_id.removeprefix("select-fam-")
        if attribute not in {a for a, _, _ in fam.CORDS}:
            return
        score = event.value
        if isinstance(score, int):
            self.query_one(f"#cost-fam-{attribute}", Static).update(
                f"{fam.cord_cost(score)} pts"
            )

    def _try_save(self) -> None:
        error = self.query_one("#fam-binding-error", Static)

        technique_value = self.query_one("#select-fam-technique", Select).value
        form_value = self.query_one("#select-fam-form", Select).value
        result: dict[str, object] = {
            "binding_technique": technique_value
            if isinstance(technique_value, str)
            else "",
            "binding_form": form_value if isinstance(form_value, str) else "",
        }

        for field_name, key, label in (
            ("input-fam-lab-total", "binding_lab_total", "Initial Binding Lab Total"),
            ("input-fam-target-level", "target_binding_level", "Target Binding Level"),
            ("input-fam-vis-spent", "vis_spent_binding", "Cumulative Vis Spent"),
        ):
            raw = self.query_one(f"#{field_name}", Input).value.strip()
            try:
                result[key] = int(raw)
            except ValueError:
                error.update(f"{label} must be a whole number.")
                return

        for attribute, _label, _blurb in fam.CORDS:
            result[attribute] = self.query_one(f"#select-fam-{attribute}", Select).value

        self.dismiss(result)
