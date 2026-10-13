"""Small prompts: confirmation, advancing the season, the list sub-dialog a
form field can open, and the short FieldsDialog forms the pickers and lists
open."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.events import Key
from textual.widgets import (
    Button,
    Label,
    OptionList,
    Static,
)
from textual.widgets.button import ButtonVariant
from textual.widgets.option_list import Option

from ... import (
    ability_forms,
    covenant_forms,
    creation,
    diary_forms,
    laboratory_forms,
    trait_forms,
    transfer,
    virtue_forms,
    vis,
    vis_forms,
)
from ... import house_rules as hr
from ... import lab_texts as lt
from ... import players as pl
from ... import saga_content as sc
from ... import saga_content_forms as scf
from ... import sheet_text as st
from ...ability_forms import ability_fields as _ability_fields
from ...ability_forms import ability_problem as _ability_problem
from ...arts import ART_DESCRIPTIONS, ARTS, FORMS, TECHNIQUES
from ...form_spec import DialogField, attr, pairs
from ...markup import escape, todo
from ...models import (
    LAB_ACTIVITIES,
    LAB_TEXT_KINDS,
    SEASONS,
    Ability,
    ArcaneConnection,
    Book,
    Character,
    Covenant,
    CovenantDiaryEntry,
    CreationConditions,
    CreationXp,
    DiaryEntry,
    Laboratory,
    LabSpecialtyEntry,
    LabVirtueFlawDef,
    MasteryAbility,
    NamedDescription,
    Player,
    Saga,
    SagaSource,
    ScoredTrait,
    VirtueFlawInstance,
    next_season,
)
from ...rules import creation_access, lab_seasons
from ...rules import xp as xp_rules
from ...rules.creation_character import age as creation_age
from ...rules.creation_covenant import (
    POWER_BY_NAME,
    POWER_LEVELS,
    PowerLevel,
    band,
    in_band,
)
from .fields import FieldsDialog, ModalDialog
from .widgets import SelectableList

#: In the core now; the terminal's pickers and lists still import them here.
_ability_from = ability_forms.ability_from
param_choices = virtue_forms.param_choices


def _date_fields(season: str, year: int) -> list[DialogField]:
    """Set the saga's date."""
    return [
        DialogField("season", "Season", "select", season, options=pairs(SEASONS)),
        DialogField("year", "Year", "int", year),
    ]


def _ability_dialog(
    name: str,
    ability: Ability | None,
    virtues_flaws: Sequence[VirtueFlawInstance] = (),
    *,
    save_label: str = "Save",
    note: str = "",
) -> FieldsDialog[dict[str, Any]]:
    """Add or edit an Ability: its xp, with the score it buys shown live
    (with the owner's Puissant, from `virtues_flaws`), and its Specialty.
    `note` follows the live line (e.g. how much xp the Creation Worksheet
    gave it)."""
    return FieldsDialog(
        escape(name),
        _ability_fields(ability),
        validate=_ability_problem,
        live=ability_forms.ability_live(name, virtues_flaws, note),
        save_label=save_label,
    )


def _boon_hook_fields(
    detail: str = "",
    description: str = "",
    *,
    can_be_unknown: bool = False,
    unknown: bool = False,
    sources: Sequence[tuple[str, str]] | None = None,
    source: str = "",
) -> list[DialogField]:
    """covenant_forms.boon_hook_fields, under the name the terminal uses."""
    return covenant_forms.boon_hook_fields(
        detail,
        description,
        can_be_unknown=can_be_unknown,
        unknown=unknown,
        sources=list(sources) if sources is not None else None,
        source=source,
    )


def _param_dialog(
    title: str,
    parameters: list[str],
    choices: dict[str, list[tuple[str, str]]] | None = None,
) -> FieldsDialog[dict[str, str]]:
    """Fill in a catalog entry's {placeholders} ("Affinity with {art}"):
    dismisses with {parameter: value}, values lower-cased. A parameter with
    `choices` is picked from them; the rest are typed."""
    return FieldsDialog(
        title,
        virtue_forms.param_fields(parameters, choices),
        save_label="Confirm",
        build=lambda values: virtue_forms.params_from(parameters, values),
    )


def _lab_choice_dialog(entry: LabVirtueFlawDef) -> FieldsDialog[dict[str, str]]:
    """Choose the Specialization a laboratory Virtue or Flaw grants points
    to, from the ones its catalog entry allows."""
    return FieldsDialog(
        entry.name,
        virtue_forms.lab_choice_fields(entry),
        save_label="Confirm",
        build=lambda values: {param: values[param] for param in entry.choices},
    )


def _lab_specialty_entry_dialog(
    existing: LabSpecialtyEntry | None = None,
) -> FieldsDialog[LabSpecialtyEntry]:
    """Points in a laboratory Specialization from a source the app doesn't
    work out itself (laboratory_forms.specialty_entry_fields)."""
    return FieldsDialog(
        "Add a Specialization source"
        if existing is None
        else "Edit a Specialization source",
        laboratory_forms.specialty_entry_fields(existing),
        save_label="Add" if existing is None else "Save",
        validate=laboratory_forms.specialty_entry_problem,
        build=laboratory_forms.specialty_entry_from,
    )


def _scored_trait_dialog(
    title: str,
    name_placeholder: str,
    existing: ScoredTrait | None = None,
    *,
    min_score: int | None = None,
    max_score: int | None = None,
    include_known: bool = False,
) -> FieldsDialog[ScoredTrait]:
    """A Personality Trait or Reputation (trait_forms.scored_trait_fields)."""
    return FieldsDialog(
        title,
        trait_forms.scored_trait_fields(
            name_placeholder,
            existing,
            min_score=min_score,
            max_score=max_score,
            include_known=include_known,
        ),
        validate=lambda values: trait_forms.score_problem(values, min_score, max_score),
        build=trait_forms.trait_from,
    )


def _mastery_ability_dialog(
    title: str, existing: MasteryAbility | None = None
) -> FieldsDialog[MasteryAbility]:
    return FieldsDialog(
        title,
        [
            DialogField(
                "name",
                "Name",
                "text",
                attr(existing, "name", ""),
                required=True,
                placeholder="e.g. Fast Casting",
            ),
            DialogField("level", "Level", "int", attr(existing, "level", 0)),
            DialogField("xp", "XP", "int", attr(existing, "xp", 0)),
        ],
        build=lambda values: MasteryAbility(**values),
    )


def _raw_vis_dialog(
    existing: tuple[str, int] | None = None,
) -> FieldsDialog[tuple[str, int]]:
    """An Art (stored lower-case) and a number of pawns."""
    return FieldsDialog(
        "Add Raw Vis" if existing is None else "Edit Raw Vis",
        vis_forms.raw_vis_fields(existing),
        save_label="Add" if existing is None else "Save",
        build=vis_forms.raw_vis_from,
    )


def _export_dialog(
    record: transfer.Record, folder: Path
) -> FieldsDialog[tuple[Path, bool]]:
    """Export a covenant, laboratory or character to a file:
    where to write it, and for a covenant whether its laboratories and
    characters go too. Builds (the file, with members?)."""
    kind = transfer.kind_of(record)

    def path_of(values: dict[str, Any]) -> Path:
        name = (values.get("file") or "").strip().strip('"')
        path = Path(name).expanduser()
        if name and not path.name.lower().endswith(".json"):
            path = path.with_name(path.name + transfer.SUFFIX)
        return path

    def problem(values: dict[str, Any]) -> str | None:
        if not (values.get("file") or "").strip():
            return "Give the file to write."
        if path_of(values).is_dir():
            return "That is a folder: add a file name."
        return None

    def live(values: dict[str, Any]) -> str:
        if problem(values):
            return ""
        path = path_of(values)
        if path.exists():
            return todo(f"{escape(path.name)} exists: it will be replaced.")
        return f"[dim]Writes {escape(str(path))}[/]"

    fields = [
        DialogField(
            "_what", "Exporting", "info", f"{transfer.KIND_LABELS[kind]}: {record.name}"
        ),
        DialogField(
            "file",
            "File",
            "text",
            str(folder / transfer.default_file_name(record)),
            hint="What it holds travels with it: a character's familiar, devices, "
            "books and Diary; a laboratory's books and devices. Import it into "
            "another saga with More's Import on that saga.",
        ),
    ]
    if kind == transfer.COVENANT:
        fields.append(
            DialogField(
                "with_members",
                "With its laboratories and characters",
                "check",
                False,
            )
        )
    return FieldsDialog(
        f"Export {escape(record.name)}",
        fields,
        save_label="Export",
        validate=problem,
        live=live,
        build=lambda values: (path_of(values), bool(values.get("with_members"))),
    )


def _player_dialog(saga: Saga, existing: Player | None) -> FieldsDialog[dict[str, Any]]:
    """Add or edit someone who can sign in to the saga from a browser
    (saga_content_forms.player_fields). Builds the values players.add /
    update take."""
    dialog = FieldsDialog(
        scf.player_title(existing),
        scf.player_fields(existing),
        validate=lambda values: scf.player_problem(saga, existing, values),
    )
    dialog.help_id = "tab-content-players"
    return dialog


def _saga_source_dialog(
    saga: Saga, existing: SagaSource | None
) -> FieldsDialog[dict[str, Any]]:
    """Add or edit a source of the saga's own
    (saga_content_forms.source_fields). Builds the values
    saga_content.add_source / update_source take."""
    dialog = FieldsDialog(
        scf.source_title(existing),
        scf.source_fields(existing),
        validate=lambda values: sc.source_problem(saga, values, existing),
    )
    dialog.help_id = "saga-content"
    return dialog


def _catalog_dialog(saga: Saga, key: str) -> FieldsDialog[dict[str, Any]]:
    """Whether the saga's pickers offer a shared catalog at all."""
    dialog = FieldsDialog(scf.catalog_title(key), scf.catalog_fields(saga, key))
    dialog.help_id = "saga-content"
    return dialog


def _hide_entry_dialog(key: str | None) -> FieldsDialog[dict[str, Any]]:
    """Which catalog to hide an entry of (the entry is picked next)."""
    dialog = FieldsDialog(
        "Hide a Catalog Entry", scf.hide_entry_fields(key), save_label="Next"
    )
    dialog.help_id = "saga-content"
    return dialog


def _sign_in_dialog(saga: Saga) -> FieldsDialog[Player]:
    """Who is there: a browser copy of a hosted app asks for a
    player's name and passcode before it opens `saga`. Dismisses with the
    player, or None if cancelled."""

    def problem(values: dict[str, Any]) -> str | None:
        if pl.sign_in(saga, values.get("name") or "", values.get("passcode") or ""):
            return None
        return "That name and passcode don't match a player of this saga."

    def signed_in(values: dict[str, Any]) -> Player:
        player = pl.sign_in(saga, values["name"], values["passcode"])
        assert player is not None  # `problem` let the form through
        return player

    dialog = FieldsDialog(
        f"Sign in to {escape(saga.name)}",
        [
            DialogField("name", "Name", "text", "", required=True),
            DialogField("passcode", "Passcode", "secret", "", required=True),
        ],
        validate=problem,
        save_label="Sign in",
        build=signed_in,
    )
    dialog.help_id = "sign-in"
    return dialog


def _house_rule_dialog(
    saga: Saga, existing: tuple[str, hr.Entry] | None
) -> FieldsDialog[dict[str, Any]]:
    """Add or edit a user-made catalog entry
    (saga_content_forms.house_rule_fields). Builds the values
    house_rules.add / update take (with "kind")."""
    return FieldsDialog(
        scf.house_rule_title(existing),
        scf.house_rule_fields(saga, existing),
        validate=lambda values: scf.house_rule_problem(saga, existing, values),
        live=lambda values: scf.house_rule_live(existing, values),
        build=lambda values: scf.house_rule_values(existing, values),
    )


def _lab_text_access_dialog(
    saga: Saga, character: Character
) -> FieldsDialog[tuple[str, int, str]]:
    """Whose raw Lab Texts a magus reads: an author -- a magus
    of the saga, or a name typed for one outside it --, the level he reads
    them to (0 forgets the author) and how he came to. Choosing an author
    he already reads fills in what is recorded. Builds (the author's key,
    level, how)."""
    magi = lt.author_options(saga, character)
    known = dict(lt.access_rows(saga, character))
    outside = [key for key in known if saga.character(key) is None]

    def recorded(values: dict[str, Any]) -> dict[str, Any]:
        access = character.lab_text_access.get(values.get("author") or "")
        if access is None:
            return {}
        return {"level": access.level, "via": access.via or None}

    def author(values: dict[str, Any]) -> str:
        return values.get("author") or (values.get("name") or "").strip()

    def problem(values: dict[str, Any]) -> str | None:
        if not author(values):
            return "Choose the author, or type the name of one outside the saga."
        if values["level"] < 0:
            return "Level can't be negative."
        return None

    return FieldsDialog(
        f"Lab Texts {escape(character.name)} reads",
        [
            DialogField(
                "_known",
                "Reads now",
                "info",
                "; ".join(known.values()) or "(only his own and general texts)",
            ),
            DialogField(
                "author",
                "Author",
                "select",
                None,
                options=magi,
                allow_blank=True,
                placeholder="(a magus of the saga)",
                fills=recorded,
            ),
            DialogField(
                "name",
                "or an author outside it",
                "text",
                outside[0] if len(outside) == 1 and not magi else "",
                show_if=lambda values: not values.get("author"),
            ),
            DialogField(
                "level",
                "Reads to level",
                "int",
                0,
                hint="0 forgets this author. A text above the level needs more "
                "decoding.",
            ),
            DialogField(
                "via",
                "How",
                "select",
                None,
                options=[("Decoded", "decoded"), ("Taught", "taught")],
                allow_blank=True,
                placeholder="(not recorded)",
            ),
        ],
        validate=problem,
        build=lambda values: (author(values), values["level"], values.get("via") or ""),
    )


def _ritual_again_dialog(
    saga: Saga, magus: Character, lab: Laboratory, text: Book
) -> FieldsDialog[tuple[str, str]]:
    """Perform a Longevity Ritual again from its Lab Text: the
    vis to pay with and whose. Refuses what the rules do (the live line says
    what it will cost and restore). Builds (the Art, whose vis)."""

    def check(values: dict[str, Any]):
        return lab_seasons.ritual_again(
            saga,
            magus,
            lab,
            text,
            values.get("vis_art") or "",
            values.get("vis_from") or "laboratory",
        )

    def live(values: dict[str, Any]) -> str:
        found, again = check(values)
        if again is None:
            return todo(escape(found[0]))
        return (
            f"{again.pawns} pawn(s) of {values['vis_art']} vis; "
            f"{escape(again.subject.name)}'s aging rolls -{again.modifier}. "
            "No season is taken."
        )

    def problem(values: dict[str, Any]) -> str | None:
        found, _ = check(values)
        return found[0] if found else None

    return FieldsDialog(
        "Perform the Longevity Ritual again",
        [
            DialogField("_text", "Lab Text", "info", text.name),
            DialogField("_by", "Performed by", "info", magus.name),
            DialogField(
                "vis_art",
                "Vis",
                "select",
                "Creo",
                options=[(art, art) for art in lab_seasons.LONGEVITY_VIS_ARTS],
            ),
            DialogField(
                "vis_from",
                "Vis from",
                "select",
                "laboratory",
                options=[
                    ("The laboratory's raw vis", "laboratory"),
                    (f"{magus.name}'s raw vis", "character"),
                    ("The covenant's vis stores", "covenant"),
                ],
            ),
        ],
        save_label="Perform",
        validate=problem,
        live=live,
        build=lambda values: (values["vis_art"], values["vis_from"]),
    )


def _lab_text_filter_dialog(current: lt.Filter) -> FieldsDialog[lt.Filter]:
    """Narrow a laboratory's Lab Texts: by kind, Technique,
    Form, a range of levels, and to those its owner can read. Everything
    left blank shows them all. Builds the Filter."""

    def build(values: dict[str, Any]) -> lt.Filter:
        return lt.Filter(
            kind=values.get("kind") or "",
            technique=values.get("technique") or "",
            form=values.get("form") or "",
            min_level=values.get("min_level"),
            max_level=values.get("max_level"),
            readable=bool(values.get("readable")),
        )

    def choice(key: str, label: str, value: str, options: Sequence[str]):
        return DialogField(
            key,
            label,
            "select",
            value or None,
            options=[(option, option) for option in options],
            allow_blank=True,
            placeholder="(any)",
        )

    return FieldsDialog(
        "Filter Lab Texts",
        [
            choice("kind", "Kind", current.kind, LAB_TEXT_KINDS),
            choice("technique", "Technique", current.technique, TECHNIQUES),
            choice("form", "Form", current.form, FORMS),
            DialogField("min_level", "Lowest level", "optint", current.min_level),
            DialogField("max_level", "Highest level", "optint", current.max_level),
            DialogField(
                "readable",
                "Readable only",
                "check",
                current.readable,
                hint="Leaves out raw texts the laboratory's owner hasn't decoded. "
                "Blank everything to show them all.",
            ),
        ],
        save_label="Filter",
        validate=lambda values: lt.filter_problem(build(values)),
        build=build,
    )


def _move_vis_dialog(
    source: str, what: vis.Held, destinations: Sequence[tuple[str, str]]
) -> FieldsDialog[tuple[int, str]]:
    """Move raw vis: how many of `what`'s pawns, and to which of
    `destinations` (vis.destinations). Builds (pawns, the destination)."""
    return FieldsDialog(
        "Move Raw Vis",
        [
            DialogField("_from", "From", "info", f"{source}: {what.label}"),
            DialogField("pawns", "Pawns", "int", what.pawns),
            DialogField(
                "destination",
                "To",
                "select",
                None,
                options=list(destinations),
                required=True,
                allow_blank=True,
                placeholder="(choose who gets it)",
                hint="A covenant takes it into its Raw Vis Store of that Art. "
                "Both Diaries record the move.",
            ),
        ],
        save_label="Move",
        validate=lambda values: vis.move_problem(what, values["pawns"]),
        build=lambda values: (values["pawns"], values["destination"]),
    )


def _family_prefix(name: str) -> str:
    """ "Area Lore: " for "Area Lore: {region}"; "" for a plain name."""
    return name.split("{", 1)[0] if "{" in name else ""


#: How much of an Ability's or Art's description the spend dialog shows.
_SPEND_DESCRIPTION_CHARS = 240


def _spend_live(
    saga: Saga,
    character: Character,
    name: str,
    xp: int | None,
    replacing: CreationXp | None,
) -> str:
    """The spend dialog's live lines for `xp` pool xp on `name`: what it
    gains (half again with an Affinity), the score that buys and the pool
    xp the next score needs, a cap warning, and what the Ability or Art
    is."""
    if not name:
        return "[dim]Choose an Ability or Art.[/]"
    lines = []
    if xp is not None and xp >= 0:
        gained, total = creation.spend_preview(character, name, xp, replacing)
        multiplier = creation_access.xp_multiplier(character, name)
        affinity = " (Affinity x1.5)" if multiplier > 1 else ""
        lines.append(f"{escape(name)}: gains {gained} xp{affinity}")
        is_art = name in ARTS
        factor = xp_rules.ART_FACTOR if is_art else xp_rules.ABILITY_FACTOR
        progress = xp_rules.progress(total, factor)
        more = creation_access.xp_giving(progress.next_total - total, multiplier)
        lines.append(f"{st.live_score(total, factor)} ({more} more pool xp)")
        cap = (
            None
            if is_art
            else creation_access.ability_cap_for(
                character, creation_age(saga, character), name
            )
        )
        if cap is not None and progress.score > cap:
            lines.append(f"[$text-error]Over the creation cap of {cap}[/]")
    if name in ARTS:
        description = ART_DESCRIPTIONS.get(name, "")
    else:
        definition = st.ability_definition(name)
        description = definition.description if definition else ""
    if description:
        if len(description) > _SPEND_DESCRIPTION_CHARS:
            description = description[: _SPEND_DESCRIPTION_CHARS - 1].rstrip() + "…"
        lines.append(f"[dim]{escape(description)}[/]")
    return "\n".join(lines)


def _creation_xp_dialog(
    title: str,
    targets: Sequence[str],
    existing: tuple[str, int] | None = None,
    *,
    xp_label: str = "Pool xp",
    saga: Saga | None = None,
    character: Character | None = None,
    replacing: CreationXp | None = None,
) -> FieldsDialog[tuple[str, int, str]]:
    """xp spent at a creation step: an Ability or Art
    from `targets` -- a family ("Area Lore: {region}") asks for its detail
    -- and how much pool xp, and an Ability's Specialty. Given the
    `character` (and `saga`), a live line shows what the xp gains and the
    score it buys; `replacing` is the entry being changed. Builds (the
    Ability or Art's name, the xp, the Specialty or "")."""
    families = [t for t in targets if "{" in t]
    target, detail = None, ""
    if existing is not None:
        name = existing[0]
        family = next((f for f in families if name.startswith(_family_prefix(f))), None)
        if name in targets:
            target = name
        elif family is not None:
            target, detail = family, name.removeprefix(_family_prefix(family))
        else:
            target = name
    options = [(t.replace("{", "(").replace("}", ")"), t) for t in targets]
    if existing is not None and target not in targets:
        options.append((existing[0], existing[0]))

    def resolved(values: dict[str, Any]) -> str:
        chosen = values["target"] or ""
        prefix = _family_prefix(chosen)
        return prefix + (values.get("detail") or "").strip() if prefix else chosen

    def problem(values: dict[str, Any]) -> str | None:
        prefix = _family_prefix(values["target"] or "")
        if prefix and not (values.get("detail") or "").strip():
            return f"Say which {prefix.rstrip(': ')}."
        if values["xp"] < 1:
            return "xp must be at least 1."
        return None

    def live(values: dict[str, Any]) -> str:
        assert saga is not None and character is not None
        return _spend_live(saga, character, resolved(values), values["xp"], replacing)

    ability = (
        next((a for a in character.abilities if a.name == existing[0]), None)
        if character is not None and existing is not None
        else None
    )
    specialty = (ability.specialty or "") if ability is not None else ""

    return FieldsDialog(
        title,
        [
            DialogField(
                "target",
                "Ability or Art",
                "select",
                target,
                options=options,
                required=True,
                allow_blank=True,
                placeholder="(choose one)",
            ),
            DialogField(
                "detail",
                "Which one",
                "text",
                detail,
                placeholder="e.g. the region, language or craft",
                show_if=lambda values: bool(_family_prefix(values["target"] or "")),
            ),
            DialogField("xp", xp_label, "int", existing[1] if existing else 5),
            DialogField(
                "specialty",
                "Specialty",
                "text",
                specialty,
                placeholder="(optional) e.g. Swords",
                show_if=lambda values: (
                    character is not None
                    and bool(values["target"])
                    and values["target"] not in ARTS
                ),
            ),
        ],
        validate=problem,
        live=live if character is not None and saga is not None else None,
        save_label="Spend" if existing is None else "Save",
        build=lambda values: (
            resolved(values),
            values["xp"],
            (values.get("specialty") or "").strip(),
        ),
    )


def _blanks_dialog(title: str, blanks: Sequence[str]) -> FieldsDialog:
    """The names a sample childhood or training package leaves blank
    ("area", "second_area", "language"), one text field each."""
    return FieldsDialog(
        title,
        [
            DialogField(
                blank, blank.replace("_", " ").capitalize(), "text", "", required=True
            )
            for blank in blanks
        ],
        save_label="Use",
    )


def _spell_level_dialog(spell_name: str) -> FieldsDialog[int]:
    """The level a General-level spell is learned at."""
    return FieldsDialog(
        f"Learn {escape(spell_name)} at what level?",
        [DialogField("level", "Level", "int", 5)],
        validate=lambda values: (
            None if values["level"] >= 1 else "Level must be at least 1."
        ),
        save_label="Learn",
        build=lambda values: values["level"],
    )


def _gauntlet_conditions_dialog(
    conditions: CreationConditions,
) -> FieldsDialog[dict[str, Any]]:
    """A magus's years past Gauntlet: the seasons of lab work,
    and the working conditions the storyguide set."""

    def problem(values: dict[str, Any]) -> str | None:
        if values["lab_seasons"] < 0:
            return "Lab seasons can't be negative."
        return None

    return FieldsDialog(
        "Years past Gauntlet",
        [
            DialogField(
                "lab_seasons",
                "Seasons of lab work",
                "int",
                conditions.lab_seasons,
                hint="Each costs 10 of that year's 30 points (4 a year: all 30).",
            ),
            DialogField("aura", "Aura", "int", conditions.aura),
            DialogField("lab_quality", "Lab quality", "int", conditions.lab_quality),
            DialogField(
                "living_conditions",
                "Living Conditions",
                "int",
                conditions.living_conditions,
                hint="Used for the aging rolls before play.",
            ),
        ],
        validate=problem,
    )


def _power_level_dialog(covenant: Covenant) -> FieldsDialog[dict[str, Any]]:
    """A new covenant's Power Level and when it was founded."""

    def label(power: PowerLevel) -> str:
        top = f"{power.most}" if power.most is not None else "+"
        cap = f"level {power.max_level}" if power.max_level is not None else "any level"
        return f"{power.name} ({power.least}-{top} BP, {cap})"

    return FieldsDialog(
        "Power Level",
        [
            DialogField(
                "power_level",
                "Power Level",
                "select",
                covenant.power_level or None,
                options=[(label(p), p.name) for p in POWER_LEVELS],
                required=True,
                allow_blank=True,
                placeholder="(choose one)",
            ),
            DialogField(
                "build_points_budget",
                "Build Points",
                "optint",
                covenant.build_points_budget,
                hint="Set by the storyguide, within the Power Level's range.",
            ),
            DialogField(
                "magi_without_lab",
                "Magi without a laboratory",
                "int",
                covenant.magi_without_lab,
                hint="Each refunds 50 Build Points. Every other magus has a "
                "free standard lab, entered or not.",
            ),
            DialogField(
                "year_founded",
                "Year Founded",
                "optint",
                covenant.year_founded,
                hint="Medium needs 10 years, High 50, Legendary 100.",
            ),
        ],
        validate=_power_level_problem,
    )


def _power_level_problem(values: dict[str, Any]) -> str | None:
    power = POWER_BY_NAME.get(values.get("power_level") or "")
    points = values.get("build_points_budget")
    if power is not None and points is not None and not in_band(power, points):
        return f"{power.name} gives {band(power)} Build Points."
    if (values.get("magi_without_lab") or 0) < 0:
        return "Magi without a laboratory can't be negative."
    return None


def _native_language_dialog(current: str = "") -> FieldsDialog[str]:
    """The character's Native Language (a Living Language, 75 xp)."""
    return FieldsDialog(
        "Native Language",
        [
            DialogField(
                "language",
                "Language",
                "text",
                current.removeprefix("Living Language: "),
                required=True,
                placeholder="e.g. German",
            )
        ],
        save_label="Save",
        build=lambda values: "Living Language: " + values["language"],
    )


def _named_description_dialog(
    title: str, name_placeholder: str, existing: NamedDescription | None = None
) -> FieldsDialog[NamedDescription]:
    """A laboratory Room or Equipment & Stores entry: a name and a
    (multi-line) description."""
    return FieldsDialog(
        title,
        laboratory_forms.named_description_fields(name_placeholder, existing),
        build=laboratory_forms.named_description_from,
    )


def _arcane_connection_dialog(
    title: str, existing: ArcaneConnection | None = None
) -> FieldsDialog[ArcaneConnection]:
    """A laboratory's Arcane Connection (laboratory_forms.connection_fields)."""
    return FieldsDialog(
        title,
        laboratory_forms.connection_fields(existing),
        build=lambda values: laboratory_forms.connection_from(values, existing),
    )


def _diary_entry_dialog(
    default_year: int,
    existing: DiaryEntry | None = None,
    default_season: str = SEASONS[0],
    activities: Sequence[str] = LAB_ACTIVITIES,
) -> FieldsDialog[DiaryEntry]:
    """Add or edit a Diary entry: a laboratory's (`activities` the lab
    activities) or a character's (the seasonal activities)."""
    return FieldsDialog(
        diary_forms.entry_title(existing),
        diary_forms.entry_fields(default_year, existing, default_season, activities),
        build=diary_forms.entry_from,
    )


def _covenant_diary_entry_dialog(
    covenant: Covenant,
    default_year: int,
    existing: CovenantDiaryEntry | None = None,
    default_season: str = SEASONS[0],
) -> FieldsDialog[CovenantDiaryEntry]:
    """Add or edit a covenant Diary entry (diary_forms.covenant_entry_fields)."""
    return FieldsDialog(
        diary_forms.entry_title(existing),
        diary_forms.covenant_entry_fields(
            covenant, default_year, existing, default_season
        ),
        validate=diary_forms.covenant_entry_problem(covenant, existing),
        build=diary_forms.covenant_entry_from(covenant, existing),
    )


class AdvanceSeasonScreen(ModalDialog[bool]):
    """Confirms advancing the saga's calendar by one season. Dismisses with
    True to advance, False (or via Escape) to leave the date alone."""

    help_id = "advance-season"

    CANCEL_RESULT = False

    DEFAULT_CSS = """
    AdvanceSeasonScreen {
        align: center middle;
    }

    #advance-dialog {
        width: 72;
        height: auto;
        padding: 1 2;
    }

    #advance-note {
        color: $text-muted;
        height: auto;
        margin-top: 1;
    }

    #advance-year-note, #advance-plans {
        height: auto;
        margin-top: 1;
    }

    #advance-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, season: str, year: int, plans: str = "") -> None:
        super().__init__()
        self.season = season
        self.year = year
        #: What happens to the season's plans (seasons.advance_summary):
        #: markup, "" for nothing to say.
        self.plans = plans

    def compose(self) -> ComposeResult:
        new_season, new_year = next_season(self.season, self.year)
        with Vertical(id="advance-dialog", classes="dialog-box"):
            yield Label("Advance Time", id="advance-title", classes="dialog-title")
            yield Static(
                f"Advance the saga from {self.season} {self.year} "
                f"to {new_season} {new_year}?",
                id="advance-message",
            )
            if self.plans:
                yield Static(self.plans, id="advance-plans")
            if new_year != self.year:
                yield Static(
                    "A new year: each covenant's surplus is added to its Wealth, "
                    "and Emergency Savings start again at 0.",
                    id="advance-year-note",
                )
            yield Static(
                "Advanced by mistake? Set Date (More on the saga) puts the date back"
                + (" (Wealth isn't changed back)." if new_year != self.year else ".")
                + (
                    " The saga is backed up first (sagas/backups in your data folder)."
                    if self.plans
                    else ""
                ),
                id="advance-note",
            )
            with Horizontal(id="advance-buttons"):
                yield Button("Advance", id="btn-advance", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-advance")


class InfoScreen(ModalDialog[None]):
    """Read-only text (markup) under a title, scrolling if long; Enter or
    Escape closes it."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("escape", "cancel", "Close"),
        ("enter", "cancel", "Close"),
    ]

    DEFAULT_CSS = """
    InfoScreen {
        align: center middle;
    }

    #info-dialog {
        width: 96;
        max-width: 100%;
        height: auto;
        max-height: 100%;
        padding: 1 2;
    }

    #info-scroll {
        height: auto;
        max-height: 32;
    }

    #info-text {
        height: auto;
    }
    """

    def __init__(self, title: str, text: str) -> None:
        super().__init__()
        self.info_title = title
        self.text = text

    def compose(self) -> ComposeResult:
        with Vertical(id="info-dialog", classes="dialog-box"):
            yield Label(self.info_title, id="info-title", classes="dialog-title")
            with VerticalScroll(id="info-scroll"):
                yield Static(self.text, id="info-text")
            yield Button("Close", id="btn-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close":
            self.action_cancel()


class ConfirmScreen(ModalDialog[bool]):
    """A Yes/No confirmation, e.g. before deleting something. Dismisses with
    True for Yes, False for No / Escape. No is focused by default so a stray
    Enter can't delete; `y` and `n` answer directly. `message` is shown as
    markup, so escape any user text in it."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("n", "no", "No"),
        ("y", "yes", "Yes"),
    ]

    DEFAULT_CSS = """
    ConfirmScreen {
        align: center middle;
    }

    #confirm-dialog {
        width: 60;
        height: auto;
        padding: 1 2;
    }

    #confirm-message {
        height: auto;
        margin-bottom: 1;
    }

    #confirm-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(
        self,
        message: str,
        *,
        yes_label: str = "Yes",
        yes_variant: ButtonVariant = "error",
        safe_answer: bool = False,
    ) -> None:
        """`safe_answer` is the answer a stray key should give: False (No) for
        the usual "Delete X?"; True when No is the risky choice, which also
        focuses Yes and makes Escape answer Yes."""
        super().__init__()
        self.message = message
        self.yes_label = yes_label
        self.yes_variant: ButtonVariant = yes_variant
        self.safe_answer = safe_answer

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog", classes="dialog-box"):
            yield Static(self.message, id="confirm-message")
            with Horizontal(id="confirm-buttons"):
                yield Button(self.yes_label, id="btn-yes", variant=self.yes_variant)
                yield Button("No", id="btn-no")

    def on_mount(self) -> None:
        self.query_one("#btn-yes" if self.safe_answer else "#btn-no", Button).focus()

    def action_cancel(self) -> None:
        """Escape: the answer a stray key should give."""
        self.dismiss(self.safe_answer)

    def action_escape(self) -> None:
        self.action_cancel()

    def action_yes(self) -> None:
        self.dismiss(True)

    def action_no(self) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-yes")


class MenuScreen(ModalDialog[str | None]):
    """A short menu of actions (the workspace's More and New):
    each item has its own letter, shown in front of it. Pressing the letter,
    or Enter on the highlighted item, dismisses with that item's key; Escape
    with None. `items` are (letter, key, label); labels are markup."""

    DEFAULT_CSS = """
    MenuScreen {
        align: center middle;
    }

    #menu-dialog {
        width: auto;
        min-width: 30;
        max-width: 76;
        height: auto;
        padding: 1 2;
    }

    #menu-list {
        width: auto;
        min-width: 24;
        height: auto;
        max-height: 16;
        border: none;
        padding: 0;
        background: transparent;
    }
    """

    def __init__(self, title: str, items: Sequence[tuple[str, str, str]]) -> None:
        super().__init__()
        self.menu_title = title
        self.items = list(items)

    def compose(self) -> ComposeResult:
        with Vertical(id="menu-dialog", classes="dialog-box"):
            yield Label(self.menu_title, id="menu-title", classes="dialog-title")
            yield OptionList(
                *(
                    Option(f"[b]{letter}[/]  {label}", id=key)
                    for letter, key, label in self.items
                ),
                id="menu-list",
                compact=True,
            )

    def on_mount(self) -> None:
        self.query_one("#menu-list", OptionList).focus()

    def on_key(self, event: Key) -> None:
        for letter, key, _ in self.items:
            if event.character == letter:
                event.stop()
                self.dismiss(key)
                return

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        event.stop()
        self.dismiss(event.option.id)


class ListFieldScreen[ItemT](ModalDialog[list[ItemT] | None]):
    """A small list edited inside a form (e.g. a device's components): its
    rows, with a to add one, e to edit the chosen row and d to delete it
    (after confirming), each entry through `dialog` (a FieldsDialog for one
    entry; None: a new one). Nothing reaches the record until the form it
    was opened from is saved: Done dismisses with the edited list,
    Escape/Cancel with None."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("a", "add", "Add"),
        Binding("e", "edit", "Edit"),
        Binding("d", "remove", "Delete"),
        Binding("delete", "remove", "Delete", show=False),
    ]

    DEFAULT_CSS = """
    ListFieldScreen {
        align: center middle;
    }

    #list-field-dialog {
        width: 84;
        max-width: 100%;
        height: auto;
        max-height: 100%;
        padding: 1 2;
    }

    #list-field-hint {
        color: $text-muted;
        height: auto;
        margin: 1 0;
    }

    #list-field-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(
        self,
        title: str,
        items: list[ItemT],
        label: Callable[[ItemT], str],
        dialog: Callable[[ItemT | None], FieldsDialog[ItemT]],
        *,
        hint: str = "",
    ) -> None:
        super().__init__()
        self.title_text = title
        self.items = list(items)
        self.label = label
        self.dialog = dialog
        self.hint = hint

    def _rows(self) -> list[tuple[int | None, str]]:
        return [(index, self.label(item)) for index, item in enumerate(self.items)]

    def compose(self) -> ComposeResult:
        with Vertical(id="list-field-dialog", classes="dialog-box"):
            yield Label(self.title_text, id="list-field-title", classes="dialog-title")
            yield SelectableList(self._rows(), id="list-field-list")
            yield Static(
                "a adds, e edits the chosen row, d deletes it."
                + (f" {self.hint}" if self.hint else ""),
                id="list-field-hint",
            )
            with Horizontal(id="list-field-buttons"):
                yield Button("Add", id="btn-add")
                yield Button("Done", id="btn-done", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#list-field-list", SelectableList).focus()

    def _chosen(self) -> int | None:
        index = self.query_one("#list-field-list", SelectableList).selected_data_index
        if index is None and len(self.items) == 1:
            return 0
        return index

    def _refill(self, choose: int | None = None) -> None:
        rows = self.query_one("#list-field-list", SelectableList)
        rows.set_rows(self._rows())
        if choose is not None:
            rows.select_data_index(choose)

    def action_add(self) -> None:
        def handle_result(item: ItemT | None) -> None:
            if item is not None:
                self.items.append(item)
                self._refill(len(self.items) - 1)

        self.app.push_screen(self.dialog(None), handle_result)

    def action_edit(self) -> None:
        index = self._chosen()
        if index is None:
            self.notify("Choose a row to edit first.")
            return

        def handle_result(item: ItemT | None) -> None:
            if item is not None:
                self.items[index] = item
                self._refill(index)

        self.app.push_screen(self.dialog(self.items[index]), handle_result)

    def action_remove(self) -> None:
        index = self._chosen()
        if index is None:
            self.notify("Choose a row to delete first.")
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                del self.items[index]
                self._refill()

        self.app.push_screen(
            ConfirmScreen(f"Delete {self.label(self.items[index])}?"),
            handle_confirmed,
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "btn-add":
            self.action_add()
        elif event.button.id == "btn-done":
            self.dismiss(list(self.items))
        elif event.button.id == "btn-cancel":
            self.action_cancel()


def _list_display(label: Callable[[Any], str]) -> Callable[[Any], str]:
    """A list field's button text (plain): its entries, or "(none)"."""

    def display(items: list[Any]) -> str:
        if not items:
            return "(none: press to add)"
        return "; ".join(label(item) for item in items)

    return display


def _list_field(
    key: str,
    label: str,
    items: list[Any],
    title: str,
    row: Callable[[Any], str],
    dialog: Callable[[Any], FieldsDialog[Any]],
    **extra: Any,
) -> DialogField:
    """A form field holding a small list: a button showing its entries that
    opens a ListFieldScreen to add, edit and delete them (`row` labels an
    entry in plain text; `dialog` edits one)."""
    return DialogField(
        key,
        label,
        "picker",
        list(items),
        picker=lambda current: ListFieldScreen(
            title, current or [], lambda item: escape(row(item)), dialog
        ),
        display=_list_display(row),
        **extra,
    )
