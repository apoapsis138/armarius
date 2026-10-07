"""The spell form (with its Range / Duration / Target choices and level)
and the Spell Mastery editor."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Label, ListItem, ListView, Static

from ... import spells as spl
from ...arts import FORMS, TECHNIQUES
from ...markup import escape
from ...models import (
    SPELL_DURATIONS,
    SPELL_RANGES,
    SPELL_TARGETS,
    KnownSpell,
    MasteryAbility,
    Spell,
)
from ...rules import spell_levels
from ..fields import DialogField, ModalDialog, _attr, _pairs
from ..prompts import ConfirmScreen, _mastery_ability_dialog

#: The choice in a Range/Duration/Target select that opens a free-text box.
_OTHER = "__other__"


def _rdt_field(
    key: str,
    label: str,
    standard: tuple[str, ...],
    value: str,
    fills: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> list[DialogField]:
    """A Range/Duration/Target select of the standard values plus "Other...",
    which shows a text box for a supplement's own value."""
    other = bool(value) and value not in standard
    return [
        DialogField(
            key,
            label,
            "select",
            _OTHER if other else value,
            options=_pairs(standard) + [("Other...", _OTHER)],
            required=True,
            allow_blank=True,
            placeholder=f"(choose a {label})",
            fills=fills,
        ),
        DialogField(
            f"{key}_other",
            f"{label} (other)",
            "text",
            value if other else "",
            placeholder="e.g. Road, Special",
            show_if=lambda v, k=key: v.get(k) == _OTHER,
        ),
    ]


def _spell_fields(spell: Spell | None) -> list[DialogField]:
    return [
        DialogField("name", "Name", "text", _attr(spell, "name", ""), required=True),
        DialogField(
            "technique",
            "Technique",
            "select",
            _attr(spell, "technique", ""),
            options=_pairs(TECHNIQUES),
            required=True,
            allow_blank=True,
            placeholder="(choose a Technique)",
        ),
        DialogField(
            "form",
            "Form",
            "select",
            _attr(spell, "form", ""),
            options=_pairs(FORMS),
            required=True,
            allow_blank=True,
            placeholder="(choose a Form)",
        ),
        DialogField(
            "level",
            "Level",
            "optint",
            _attr(spell, "level", None),
            hint="Leave blank for a General spell (cast at any level).",
        ),
        DialogField(
            "requisites",
            "Requisites",
            "text",
            ", ".join(_attr(spell, "requisites", [])),
            placeholder="e.g. Rego, Corpus",
        ),
        *_rdt_field(
            "range", "Range", SPELL_RANGES, _attr(spell, "range", ""), _level_fill
        ),
        *_rdt_field(
            "duration",
            "Duration",
            SPELL_DURATIONS,
            _attr(spell, "duration", ""),
            _level_fill,
        ),
        *_rdt_field(
            "target", "Target", SPELL_TARGETS, _attr(spell, "target", ""), _level_fill
        ),
        DialogField("ritual", "Ritual", "check", _attr(spell, "ritual", False)),
        DialogField(
            "base_level",
            "Base level",
            "optint",
            _attr(spell, "base_level", None),
            hint="The guideline's level; with Range, Duration and Target it "
            "fills in Level (add any size or requisite magnitudes yourself).",
            fills=_level_fill,
        ),
        DialogField(
            "source",
            "Source",
            "text",
            _attr(spell, "source", ""),
            placeholder="e.g. a house rule, or a book",
        ),
        DialogField(
            "description", "Description", "area", _attr(spell, "description", "")
        ),
    ]


def _level_fill(values: dict[str, Any]) -> dict[str, Any]:
    """Level worked out from the base and Range/Duration/Target
    (rules.spell_levels), once they are all standard and given."""
    base = values.get("base_level")
    if base is None:
        return {}
    design = spell_levels.spell_level(
        base,
        _spell_rdt(values, "range"),
        _spell_rdt(values, "duration"),
        _spell_rdt(values, "target"),
        ritual=bool(values.get("ritual")),
    )
    return {} if design is None else {"level": design.level}


def _spell_rdt(values: dict[str, Any], key: str) -> str:
    chosen = values.get(key) or ""
    return values.get(f"{key}_other", "").strip() if chosen == _OTHER else chosen


def _spell_from_values(spell: Spell, values: dict[str, Any]) -> None:
    spell.name = values["name"]
    spell.technique = values["technique"]
    spell.form = values["form"]
    spell.level = values.get("level")
    spell.requisites = spl.parse_requisites(values.get("requisites", ""))
    spell.range = _spell_rdt(values, "range")
    spell.duration = _spell_rdt(values, "duration")
    spell.target = _spell_rdt(values, "target")
    spell.ritual = bool(values.get("ritual"))
    spell.base_level = values.get("base_level")
    spell.source = values.get("source", "")
    spell.description = values.get("description", "")
    spell.details_missing = False


def _spell_problem(values: dict[str, Any]) -> str | None:
    if values.get("level") is not None and values["level"] < 1:
        return "Level must be at least 1 (or blank for a General spell)."
    for key, label in (
        ("range", "Range"),
        ("duration", "Duration"),
        ("target", "Target"),
    ):
        if values.get(key) == _OTHER and not values.get(f"{key}_other", "").strip():
            return f"Type the {label}, or choose one of the standard ones."
    unknown = spl.unknown_requisites(values.get("requisites", ""))
    if unknown:
        return f"Requisites must be Arts (e.g. Rego, Corpus), not {', '.join(unknown)}."
    return None


def _spell_live(values: dict[str, Any]) -> str:
    """The form's live line: the spell's shorthand and magnitude."""
    if not values.get("technique") or not values.get("form"):
        return "[dim]Choose a Technique and a Form.[/]"
    probe = Spell(
        id="",
        name="",
        technique=values["technique"],
        form=values["form"],
        level=values.get("level"),
        requisites=spl.parse_requisites(values.get("requisites", "")),
        ritual=bool(values.get("ritual")),
    )
    mag = spl.magnitude(probe)
    text = f"[b]{escape(spl.shorthand(probe))}[/]"
    text += "  General level" if mag is None else f"  magnitude {mag}"
    if probe.ritual and mag is not None:
        text += f"  ({spl.vis_cost(probe)} pawns, {spl.casting_time(probe)})"
    return text


class MasteryEditScreen(ModalDialog[KnownSpell | None]):
    """Edits a known spell's Mastery: score, xp, and its Mastery Abilities
    (each with its own name/level/xp -- see MasteryAbility). Abilities are
    added/removed here and only committed to the character on Save.
    Dismisses with the finished KnownSpell, or None if cancelled."""

    DEFAULT_CSS = """
    MasteryEditScreen {
        align: center middle;
    }

    #mastery-dialog {
        width: 70;
        height: auto;
        max-height: 30;
        padding: 1 2;
    }

    #mastery-abilities-list {
        height: auto;
        max-height: 8;
        border: solid $accent;
    }

    #mastery-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #mastery-ability-row-buttons {
        width: 100%;
        height: auto;
    }

    #mastery-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, spell_name: str, existing: KnownSpell) -> None:
        super().__init__()
        self.spell_name = spell_name
        self.spell_id = existing.spell_id
        self.mastery_score = existing.mastery_score
        self.mastery_xp = existing.mastery_xp
        #: A working copy -- only becomes real on Save.
        self._abilities: list[MasteryAbility] = list(existing.mastery_abilities)

    def compose(self) -> ComposeResult:
        with Vertical(id="mastery-dialog", classes="dialog-box"):
            yield Label(
                f"Mastery: {escape(self.spell_name)}",
                id="mastery-title",
                classes="dialog-title",
            )
            yield Label("Score")
            yield Input(
                value=str(self.mastery_score), type="integer", id="input-mastery-score"
            )
            yield Label("XP")
            yield Input(
                value=str(self.mastery_xp), type="integer", id="input-mastery-xp"
            )
            yield Label("Mastery Abilities")
            yield ListView(id="mastery-abilities-list")
            with Horizontal(id="mastery-ability-row-buttons"):
                yield Button("Add Ability", id="btn-add-ability", compact=True)
                yield Button("Remove Ability", id="btn-remove-ability", compact=True)
            yield Static("", id="mastery-error")
            with Horizontal(id="mastery-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        self._render_abilities()

    def _render_abilities(self) -> None:
        list_view = self.query_one("#mastery-abilities-list", ListView)
        list_view.clear()
        if not self._abilities:
            list_view.append(ListItem(Label("[dim](none)[/]")))
            return
        for ability in self._abilities:
            list_view.append(
                ListItem(Label(f"{escape(ability.name)} {ability.level}/{ability.xp}"))
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-save":
            self._try_save()
        elif event.button.id == "btn-add-ability":
            self._add_ability()
        elif event.button.id == "btn-remove-ability":
            self._remove_ability()

    def _add_ability(self) -> None:
        def handle_result(ability: MasteryAbility | None) -> None:
            if ability is not None:
                self._abilities.append(ability)
                self._render_abilities()

        self.app.push_screen(
            _mastery_ability_dialog("Add a Mastery Ability"), handle_result
        )

    def _remove_ability(self) -> None:
        if not self._abilities:
            return
        list_view = self.query_one("#mastery-abilities-list", ListView)
        index = list_view.index
        if index is None or index >= len(self._abilities):
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                del self._abilities[index]
                self._render_abilities()

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(self._abilities[index].name)}?"),
            handle_confirmed,
        )

    def _try_save(self) -> None:
        error = self.query_one("#mastery-error", Static)
        try:
            score = int(self.query_one("#input-mastery-score", Input).value)
            xp = int(self.query_one("#input-mastery-xp", Input).value)
        except ValueError:
            error.update("Score and XP must be whole numbers.")
            return
        self.dismiss(
            KnownSpell(
                spell_id=self.spell_id,
                mastery_score=score,
                mastery_xp=xp,
                mastery_abilities=self._abilities,
            )
        )
