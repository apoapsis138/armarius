"""Every Textual screen, dialog and widget: the saga picker, the workspace
(navigation tree + sheet pane), the Character/Laboratory/Familiar/Covenant
sheets, the Book and Spell lists, and the add/edit dialogs and pickers."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from functools import cached_property, partial
from pathlib import Path
from typing import Any, ClassVar, NamedTuple, cast

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.content import Content
from textual.css.query import NoMatches
from textual.events import Click, DescendantBlur, DescendantFocus, Key
from textual.message import Message
from textual.screen import ModalScreen, Screen
from textual.widget import Widget
from textual.widgets import (
    Button,
    Checkbox,
    Collapsible,
    DirectoryTree,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    OptionList,
    Select,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
    Tree,
)
from textual.widgets._collapsible import CollapsibleTitle
from textual.widgets.option_list import Option

from . import books as bk
from . import catalog, storage
from . import economics as eco
from . import familiars as fam
from . import inhabitants as inh
from . import possessions as pos
from . import sheet_text as st
from . import spells as spl
from .markup import aligned, escape, markdown_inline
from .models import (
    ART_ABBREVIATIONS,
    ART_DESCRIPTIONS,
    ARTS,
    BOOK_TYPES,
    BOON_HOOK_DESCRIPTION,
    BOON_HOOK_DETAIL,
    CORD_SCORE_COSTS,
    COVENANT_ROLES,
    CRAFT_FIELDS,
    FATIGUE_LEVELS,
    FORMS,
    GEAR_QUALITIES,
    GEAR_QUALITY_DEFAULT,
    GEAR_TYPES_BY_KIND,
    GIFT_CHOICES,
    INCOME_EFFECTS,
    INCOME_TYPE_DEFAULTS,
    INCOME_TYPES,
    INHABITANT_KINDS,
    LAB_CHARACTERISTICS,
    LOYALTY_EQUIPMENT,
    LOYALTY_MONEY,
    OTHER_COVENFOLK_ROLES,
    POSSESSION_KINDS,
    SANCTUM_USAGE_DEFAULT,
    SANCTUM_USAGES,
    SEASONS,
    SPELL_DURATIONS,
    SPELL_RANGES,
    SPELL_SOURCES,
    SPELL_TARGETS,
    TECHNIQUES,
    TRACTATUS_SUBJECTS,
    Ability,
    AbilityDef,
    Aging,
    ArtScore,
    Background,
    BondPower,
    Book,
    Character,
    Characteristics,
    Covenant,
    CovenantBoonHookDef,
    Description,
    DiaryEntry,
    Familiar,
    FatigueLevel,
    HermeticBackground,
    IncomeSource,
    KnownSpell,
    LabCharacteristics,
    Laboratory,
    LabVirtueFlawDef,
    MasteryAbility,
    NamedDescription,
    Possession,
    Saga,
    ScoredTrait,
    Spell,
    VirtueFlawDef,
    VirtueFlawInstance,
    Wounds,
    add_raw_vis,
    assign_laboratory,
    assign_laboratory_owner,
    boon_hook_params,
    character_age,
    covenant_boon_points,
    covenant_effective_aura,
    covenant_hook_points,
    lab_aura_total,
    lab_base_safety,
    lab_characteristic_total,
    lab_free_virtues,
    lab_occupied_size,
    next_season,
    replace_raw_vis,
)

_SAGA_ITEM_ID_PREFIX = "saga-"
_VIRTUE_FLAW_ITEM_ID_PREFIX = "vf-"
_LAB_VIRTUE_FLAW_ITEM_ID_PREFIX = "labvf-"
_ABILITY_ITEM_ID_PREFIX = "ability-"
_REMOVAL_ITEM_ID_PREFIX = "remove-"
_COVENANT_BOON_HOOK_ITEM_ID_PREFIX = "covbhpick-"


def _balance_colour(boon_points: float, hook_points: float) -> str:
    """Colour for the Boons/Hooks point totals, shared by both: cyan while
    Boons cost less than Hooks provide, red once they cost more, green when
    they exactly balance."""
    if boon_points < hook_points:
        return "cyan"
    if boon_points > hook_points:
        return "red"
    return "green"


def _tier_text(entry: CovenantBoonHookDef) -> str:
    """ "Minor Boon (1 pt)", "Major Hook (3 pts)" or "Free Boon"."""
    points = abs(entry.cost)
    if not points:
        return f"{entry.tier} {entry.type}"
    return f"{entry.tier} {entry.type} ({points:g} {'pt' if points == 1 else 'pts'})"


def _year_born_field(value: int | None) -> DialogField:
    """Year Born is never required: blank means Unknown."""
    return DialogField("year_born", "Year Born (blank = Unknown)", "optint", value)


def _inhabitant_fields(
    kind: str,
    entry: inh.InhabitantEntry | None,
    grog: Character | None,
) -> list[DialogField]:
    """The add/edit form for one kind of inhabitant. For a person listed from a
    character sheet, name/house/year are shown read-only (edit them on the
    sheet) and only the covenant-side fields are editable."""
    auto = entry is not None and entry.auto
    character = entry.character if entry is not None else grog
    houses = [(h.name, h.id) for h in catalog.load_house_catalog()]
    fields: list[DialogField] = []

    if auto and entry is not None:
        fields.append(
            DialogField(
                "_n", "Name", "info", f"{entry.name} (from the character sheet)"
            )
        )
        if kind == "magus":
            fields.append(
                DialogField(
                    "_h", "House", "info", inh.house_name(entry.house_id) or "Unknown"
                )
            )
        year = entry.year_born
        fields.append(
            DialogField("_y", "Year Born", "info", "Unknown" if year is None else year)
        )
        if kind == "magus":
            fields.append(DialogField("_g", "Gift", "info", entry.gift))
    else:
        name = entry.name if entry is not None else (grog.name if grog else "")
        year_born = (
            entry.year_born
            if entry is not None
            else (grog.background.year_born if grog else None)
        )
        fields.append(DialogField("name", "Name", "text", name, required=True))
        if kind == "magus":
            fields.append(
                DialogField(
                    "house",
                    "House",
                    "select",
                    entry.house_id if entry else None,
                    options=houses,
                    allow_blank=True,
                    placeholder="Unknown",
                )
            )
        fields.append(_year_born_field(year_born))
        if kind == "magus":
            fields.append(
                DialogField(
                    "gift",
                    "Gift",
                    "select",
                    entry.record.gift if entry and entry.record else "",
                    options=[(c, c) for c in GIFT_CHOICES],
                    allow_blank=True,
                    placeholder="Unknown (assumed The Gift)",
                )
            )

    if kind in ("companion", "specialist", "craftsperson", "turb", "inhabitant"):
        fields.append(
            DialogField(
                "responsibility",
                "Responsibility",
                "text",
                entry.responsibility if entry else "",
            )
        )
    if kind in ("companion", "specialist"):
        fields.append(
            DialogField(
                "role",
                "Covenant Role",
                "select",
                entry.role if entry else "",
                options=[(r, r) for r in COVENANT_ROLES],
                allow_blank=True,
            )
        )
        # Steward/Chamberlain/Turb Captain/Autocrat earn the covenant a
        # Loyalty bonus (Presence + a specific Ability). The role has to be
        # chosen and saved first -- editing again then shows this.
        if entry is not None and entry.role in inh.ROLE_ABILITY_MAP:
            ability_label = " + ".join(inh.ROLE_ABILITY_MAP[entry.role])
            if entry.character is not None:
                fields.append(
                    DialogField(
                        "_rb",
                        "Loyalty Bonus",
                        "info",
                        f"{entry.role_bonus} (Presence {entry.role_presence:+d}, "
                        f"{ability_label} {entry.role_ability_total}, from the "
                        "character sheet)",
                    )
                )
            else:
                fields += [
                    DialogField(
                        "presence",
                        "Presence (for the Loyalty Bonus)",
                        "int",
                        entry.record.presence if entry.record else 0,
                    ),
                    DialogField(
                        "skill_value",
                        f"{ability_label} (for the Loyalty Bonus)",
                        "int",
                        entry.record.skill_value if entry.record else 0,
                    ),
                ]
    if kind == "inhabitant":
        fields.append(
            DialogField(
                "role",
                "Covenant Role",
                "select",
                entry.role if entry else "",
                options=[(r, r) for r in OTHER_COVENFOLK_ROLES],
                required=True,
                allow_blank=True,
                placeholder="(choose a Covenant Role)",
            )
        )
    if kind == "craftsperson":
        from_ability = entry.skill_from_ability if entry is not None else None
        if from_ability is not None and entry is not None:
            # Tied to a sheet's Ability: the score is that Ability's Level.
            fields.append(
                DialogField(
                    "_s",
                    "Value of Crafting Skill",
                    "info",
                    f"{from_ability} (Level of {entry.linked_ability})",
                )
            )
        else:
            fields.append(
                DialogField(
                    "skill_value",
                    "Value of Crafting Skill",
                    "int",
                    entry.record.skill_value if entry and entry.record else 0,
                )
            )
        fields += [
            DialogField(
                "field_of_work",
                "Field of Work",
                "select",
                entry.field_of_work if entry else "None",
                options=[(f, f) for f in CRAFT_FIELDS],
            ),
            DialogField("rare", "Rare", "check", entry.rare if entry else False),
        ]
        abilities = inh.ability_names(character)
        current = entry.linked_ability if entry else ""
        if character is not None:
            options = [(a, a) for a in abilities]
            if current and current not in abilities:
                options.append((current, current))
            fields.append(
                DialogField(
                    "linked_ability",
                    "Linked Ability",
                    "select",
                    current,
                    options=options,
                    allow_blank=True,
                )
            )
        else:
            fields.append(
                DialogField("linked_ability", "Linked Ability", "text", current)
            )
    if kind not in inh.AUTO_KINDS:
        fields.append(
            DialogField("quantity", "Quantity", "int", entry.quantity if entry else 1)
        )
    fields.append(
        DialogField(
            "description",
            "Description",
            "area",
            entry.description if entry else "",
            hint="Supports **bold** and *italic*.",
        )
    )
    return fields


def _possession_fields(
    kind: str, entry: pos.PossessionEntry | None
) -> list[DialogField]:
    """The add/edit form for one kind of possession. For a laboratory listed as
    a sanctum, name/owner/location/build points are shown read-only (edit them
    on the laboratory) and only the covenant-side fields are editable."""
    fields: list[DialogField] = []
    auto = entry is not None and entry.auto

    def value(attribute: str, default):
        return getattr(entry, attribute) if entry is not None else default

    if auto and entry is not None:
        note = " (from the laboratory)"
        fields.append(DialogField("_n", "Name", "info", entry.name + note))
        fields.append(
            DialogField("_o", "Owner", "info", (entry.owner or "(none)") + note)
        )
        fields.append(
            DialogField("_l", "Location", "info", entry.location or "(not set)")
        )
        fields.append(
            DialogField(
                "_b",
                "Build Points",
                "info",
                "(not set)" if entry.build_points is None else entry.build_points,
            )
        )
        if kind == "sanctum":
            fields.append(
                DialogField("_q", "Quality", "info", str(entry.quality) + note)
            )
            fields.append(
                DialogField("_u", "Upkeep (Points)", "info", str(entry.upkeep) + note)
            )
    else:
        fields.append(
            DialogField("name", "Name", "text", value("name", ""), required=True)
        )

    if kind == "property":
        fields += [
            DialogField("location", "Location", "text", value("location", "")),
            DialogField("dimensions", "Dimensions", "text", value("dimensions", "")),
            DialogField("inhabitants", "Inhabitants", "text", value("inhabitants", "")),
        ]
    elif kind == "sanctum":
        if not auto:
            fields += [
                # Unowned sanctums are "Free": narratively, visitors can use them.
                DialogField("owner", "Owner", "text", value("owner", "Free")),
                DialogField("location", "Location", "text", value("location", "")),
                DialogField("quality", "Quality", "optint", value("quality", None)),
                DialogField(
                    "upkeep", "Upkeep (Points)", "optint", value("upkeep", None)
                ),
                DialogField(
                    "build_points",
                    "Build Points",
                    "optint",
                    value("build_points", None),
                ),
            ]
        fields.append(
            DialogField(
                "usage",
                "Usage",
                "select",
                value("usage", SANCTUM_USAGE_DEFAULT),
                options=[(u, u) for u in SANCTUM_USAGES],
            )
        )
    elif kind in pos.QUANTITY_KINDS:
        if kind in GEAR_TYPES_BY_KIND:
            types = GEAR_TYPES_BY_KIND[kind]
            fields += [
                DialogField(
                    "gear_type",
                    "Type",
                    "select",
                    value("gear_type", types[0]) or types[0],
                    options=[(t, t) for t in types],
                ),
                DialogField(
                    "gear_quality",
                    "Quality",
                    "select",
                    value("gear_quality", GEAR_QUALITY_DEFAULT),
                    options=[(q, q) for q in GEAR_QUALITIES],
                ),
            ]
        fields.append(DialogField("quantity", "Quantity", "int", value("quantity", 1)))
        if kind == "weapon":
            fields += [
                DialogField("weapon_init", "Init", "int", value("weapon_init", 0)),
                DialogField(
                    "weapon_attack", "Attack", "int", value("weapon_attack", 0)
                ),
                DialogField(
                    "weapon_defense", "Defense", "int", value("weapon_defense", 0)
                ),
                DialogField(
                    "weapon_damage", "Damage", "int", value("weapon_damage", 0)
                ),
            ]
    elif kind in ("vis_source", "vis_store"):
        fields.append(
            DialogField(
                "art",
                "Art",
                "select",
                value("art", ""),
                options=[(a, a) for a in ARTS],
                required=True,
                allow_blank=True,
                placeholder="(choose an Art)",
            )
        )
        if kind == "vis_source":
            fields.append(
                DialogField(
                    "season",
                    "Season harvested",
                    "select",
                    value("season", ""),
                    options=[(x, x) for x in SEASONS],
                    required=True,
                    allow_blank=True,
                    placeholder="(choose a Season)",
                )
            )
        fields += [
            DialogField("pawns", "Pawns", "int", value("pawns", 1) or 1),
            DialogField("location", "Location", "text", value("location", "")),
            DialogField(
                "physical_form", "Physical Form", "text", value("physical_form", "")
            ),
        ]

    if kind != "vis_store":
        fields.append(
            DialogField(
                "description",
                "Description",
                "area",
                value("description", ""),
                hint="Supports **bold** and *italic*.",
            )
        )
    return fields


def _bond_power_fields(power: BondPower | None) -> list[DialogField]:
    """The add/edit form for one Empowered Bond Power -- all typed-in, no
    Lab Total formula computed (see BondPower's docstring)."""

    def value(attribute: str, default):
        return getattr(power, attribute) if power is not None else default

    return [
        DialogField("name", "Power Name", "text", value("name", ""), required=True),
        DialogField("level", "Level", "int", value("level", 0)),
        DialogField(
            "technique",
            "Technique",
            "select",
            value("technique", ""),
            options=[(t, t) for t in TECHNIQUES],
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField(
            "form",
            "Form",
            "select",
            value("form", ""),
            options=[(f, f) for f in FORMS],
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField(
            "target_controller",
            "Target & Controller",
            "text",
            value("target_controller", ""),
            placeholder="e.g. Magus (controlled by Familiar)",
        ),
        DialogField("uses_per_day", "Uses/Day", "int", value("uses_per_day", 0)),
        DialogField("penetration", "Penetration", "int", value("penetration", 0)),
        DialogField("vis_spent", "Vis Spent", "int", value("vis_spent", 0)),
        DialogField(
            "cosmetic_trait",
            "Cosmetic Trait Manifested",
            "text",
            value("cosmetic_trait", ""),
        ),
    ]


def _ability_template_prefix(name: str) -> str | None:
    """ "Area Lore: " for a templated catalog name like "Area Lore: {region}"."""
    return name.split("{", 1)[0] if "{" in name else None


def _book_ability_choice(ability: str, names: list[str]) -> tuple[str, str]:
    """(Ability select value, Ability detail) for a book's stored ability: a
    catalog name as is, or a templated family plus the filled-in blank."""
    if not ability or ability in names:
        return ability, ""
    for name in names:
        prefix = _ability_template_prefix(name)
        if prefix and ability.startswith(prefix):
            return name, ability[len(prefix) :]
    return ability, ""  # not in the catalog: kept as its own option


def _book_fields(
    saga: Saga, book: Book | None, default_owner: str
) -> list[DialogField]:
    """The add/edit form for a book. Which of Art/Ability/Spell, Level and
    Quality are shown follows the Type (and a Tractatus's Subject) live."""

    def value(attribute: str, default):
        return getattr(book, attribute) if book is not None else default

    ability_names = [a.name for a in catalog.load_ability_catalog()]
    ability, ability_detail = _book_ability_choice(value("ability", ""), ability_names)
    ability_options = [(n, n) for n in ability_names]
    if ability and ability not in ability_names:
        ability_options.insert(0, (ability, ability))

    def book_type(values: dict[str, Any]) -> str:
        return values.get("type") or ""

    def art_book(values: dict[str, Any]) -> bool:
        return bk.is_art_book(book_type(values), values.get("subject_kind") or "")

    def ability_book(values: dict[str, Any]) -> bool:
        return bk.is_ability_book(book_type(values), values.get("subject_kind") or "")

    def templated(values: dict[str, Any]) -> bool:
        return ability_book(values) and "{" in (values.get("ability") or "")

    # A Lab Text / Casting Tablet takes its spell's Level; only a General (or
    # not yet chosen) spell needs the book's own.
    linked = bk.book_spell(saga, book) if book is not None else None
    spell_id = linked.id if linked is not None else None

    def spell_display(chosen_id: str) -> str:
        spell = spl.find_spell(saga, chosen_id)
        if spell is None:
            return chosen_id
        return f"{spell.name}  ({spl.shorthand(spell)})"

    def needs_level(values: dict[str, Any]) -> bool:
        kind = book_type(values)
        if kind not in bk.SPELL_TYPES:
            return bk.has_level(kind)
        spell = spl.find_spell(saga, values.get("spell_id"))
        if spell is None:
            # No spell chosen: ask for the spell first -- unless this is a book
            # whose typed spell is unknown, which keeps its own Level.
            return bool(value("spell_name", ""))
        return spell.level is None

    if book is None:
        owner = default_owner
    elif bk.is_unassigned(saga, book):
        owner = ""
    else:
        owner = bk.owner_value(book.owner_kind, book.owner_id)
    return [
        DialogField("name", "Name", "text", value("name", ""), required=True),
        DialogField(
            "type",
            "Type",
            "select",
            value("type", ""),
            options=[(t, t) for t in BOOK_TYPES],
            required=True,
            allow_blank=True,
            placeholder="(choose a Type)",
        ),
        DialogField(
            "subject_kind",
            "Subject",
            "select",
            value("subject_kind", ""),
            options=[(t, t) for t in TRACTATUS_SUBJECTS],
            required=True,
            allow_blank=True,
            placeholder="(Art or Ability)",
            show_if=lambda v: book_type(v) == "Tractatus",
        ),
        DialogField(
            "art",
            "Art",
            "select",
            value("art", ""),
            options=[(a, a) for a in ARTS],
            required=True,
            allow_blank=True,
            placeholder="(choose an Art)",
            show_if=art_book,
        ),
        DialogField(
            "ability",
            "Ability",
            "select",
            ability,
            options=ability_options,
            required=True,
            allow_blank=True,
            placeholder="(choose an Ability)",
            show_if=ability_book,
        ),
        DialogField(
            "ability_detail",
            "Ability detail",
            "text",
            ability_detail,
            placeholder="fills the {blank}, e.g. Rhine Tribunal",
            show_if=templated,
        ),
        DialogField(
            "spell_id",
            "Spell",
            "picker",
            spell_id,
            placeholder=(
                f"Unknown: {value('spell_name', '')} -- choose the spell..."
                if spell_id is None and value("spell_name", "")
                else "(choose the spell...)"
            ),
            picker=lambda _current: SpellChooserScreen(saga),
            display=spell_display,
            show_if=lambda v: book_type(v) in bk.SPELL_TYPES,
        ),
        DialogField(
            "level",
            "Level",
            "optint",
            value("level", None),
            required=True,
            hint="",
            show_if=needs_level,
        ),
        DialogField(
            "quality",
            "Quality",
            "optint",
            value("quality", None),
            required=True,
            show_if=lambda v: bk.has_quality(book_type(v)),
        ),
        DialogField("language", "Language", "text", value("language", "Latin")),
        DialogField("author", "Author", "text", value("author", "")),
        DialogField(
            "year_published",
            "Year Published",
            "optint",
            value("year_published", None),
        ),
        DialogField("owner", "Owner", "select", owner, options=bk.owner_options(saga)),
        DialogField(
            "description",
            "Description",
            "area",
            value("description", ""),
            hint="Supports **bold** and *italic*.",
        ),
    ]


def _book_from_values(book: Book, values: dict[str, Any], saga: Saga) -> None:
    """Write a book form's result onto `book`. Fields the chosen Type doesn't
    use (hidden in the form, so absent from `values`) are cleared."""
    book.name = values["name"]
    book.type = values["type"]
    book.language = values.get("language", "")
    book.author = values.get("author", "")
    book.year_published = values.get("year_published")
    book.description = values.get("description", "")
    book.owner_kind, book.owner_id = bk.parse_owner_value(values.get("owner"))
    book.subject_kind = values.get("subject_kind") or ""
    book.art = values.get("art") or ""
    ability = values.get("ability") or ""
    prefix = _ability_template_prefix(ability)
    if prefix is not None:
        ability = prefix + values.get("ability_detail", "")
    book.ability = ability
    book.spell_id = values.get("spell_id") if book.type in bk.SPELL_TYPES else None
    if book.type not in bk.SPELL_TYPES:
        book.spell_name = ""
    book.level = values.get("level")
    spell = spl.find_spell(saga, book.spell_id)
    if spell is not None:
        # A copy for display without the saga; level_of() reads the spell.
        book.spell_name = spell.name
        if spell.level is not None:
            book.level = spell.level
    book.quality = values.get("quality")


def _book_live(values: dict[str, Any], saga: Saga) -> str:
    """The form's live line: the Build Point cost (a Lab Text's or Casting
    Tablet's from its spell's level) and any covenant-creation limit the
    values go over (a warning, not an error)."""
    if not values.get("type"):
        return "[dim]Cost: choose a Type.[/]"
    probe = Book(id="", name="", type=values["type"])
    probe.level = values.get("level") if bk.has_level(probe.type) else None
    probe.quality = values.get("quality") if bk.has_quality(probe.type) else None
    probe.spell_id = values.get("spell_id") if probe.type in bk.SPELL_TYPES else None
    lines = [f"[b]Cost:[/] {bk.cost(probe, saga)} Build Points"]
    spell = spl.find_spell(saga, probe.spell_id)
    if spell is not None and spell.level is not None:
        lines[0] += f"  [dim](Level {spell.level}, from the spell)[/]"
    lines += [f"[red]{escape(w)}[/]" for w in bk.limit_warnings(probe)]
    return "\n".join(lines)


#: The choice in a Range/Duration/Target select that opens a free-text box.
_OTHER = "__other__"


def _rdt_field(
    key: str, label: str, standard: tuple[str, ...], value: str
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
            options=[(v, v) for v in standard] + [("Other...", _OTHER)],
            required=True,
            allow_blank=True,
            placeholder=f"(choose a {label})",
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
    def value(attribute: str, default):
        return getattr(spell, attribute) if spell is not None else default

    return [
        DialogField("name", "Name", "text", value("name", ""), required=True),
        DialogField(
            "technique",
            "Technique",
            "select",
            value("technique", ""),
            options=[(t, t) for t in TECHNIQUES],
            required=True,
            allow_blank=True,
            placeholder="(choose a Technique)",
        ),
        DialogField(
            "form",
            "Form",
            "select",
            value("form", ""),
            options=[(f, f) for f in FORMS],
            required=True,
            allow_blank=True,
            placeholder="(choose a Form)",
        ),
        DialogField(
            "level",
            "Level",
            "optint",
            value("level", None),
            hint="Leave blank for a General spell (cast at any level).",
        ),
        DialogField(
            "requisites",
            "Requisites",
            "text",
            ", ".join(value("requisites", [])),
            placeholder="e.g. Rego, Corpus",
        ),
        *_rdt_field("range", "Range", SPELL_RANGES, value("range", "")),
        *_rdt_field("duration", "Duration", SPELL_DURATIONS, value("duration", "")),
        *_rdt_field("target", "Target", SPELL_TARGETS, value("target", "")),
        DialogField("ritual", "Ritual", "check", value("ritual", False)),
        DialogField("base_level", "Base level", "optint", value("base_level", None)),
        DialogField(
            "source",
            "Source",
            "text",
            value("source", ""),
            placeholder="e.g. a house rule, or a book",
        ),
        DialogField("description", "Description", "area", value("description", "")),
    ]


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


def _boon_hook_names(ids: list[str], by_id: dict[str, CovenantBoonHookDef]) -> str:
    """Names of catalog entries, each listed once (Road/Urban exist at both
    tiers), for prerequisite/exclusion notes."""
    return ", ".join(dict.fromkeys(by_id[i].name for i in ids if i in by_id))


#: Covenant Reputations run from -3 to +3.
_COVENANT_REPUTATION_RANGE = (-3, 3)


class _SectionOps(NamedTuple):
    """What the a / A / e / r keys do in one sheet section (None: nothing,
    and the key is disabled there). See WorkspaceScreen._section_ops()."""

    add: Callable[[], None] | None = None
    remove: Callable[[], None] | None = None
    edit: Callable[[], None] | None = None
    restore: Callable[[], None] | None = None


@dataclass(frozen=True)
class _TraitList:
    """One of the sheets' scored-trait lists -- a record's Personality Traits
    or Reputations -- for WorkspaceScreen's shared add/edit/remove."""

    owner: str  # the WorkspaceScreen attribute holding the record
    attr: str  # the record's list: "personality_traits" or "reputations"
    section: str
    noun: str  # "Personality Trait" or "Reputation"
    example: str
    selected: str  # the WorkspaceScreen method giving the chosen row's index
    signed: bool = True  # scores shown as "+2" (not "2") in the picker
    confirm_remove: bool = True
    prompt_options: dict[str, Any] = dataclass_field(default_factory=dict)


_CHARACTER_TRAITS = _TraitList(
    "selected_character",
    "personality_traits",
    "section-personality-traits",
    "Personality Trait",
    "e.g. Brave",
    "_selected_personality_trait",
)
_CHARACTER_REPUTATIONS = _TraitList(
    "selected_character",
    "reputations",
    "section-reputations",
    "Reputation",
    "e.g. Skilled Enchanter",
    "_selected_character_reputation",
    signed=False,  # unlike every other Reputation list (STORY-1109 B14)
)
_FAMILIAR_TRAITS = _TraitList(
    "selected_familiar",
    "personality_traits",
    "section-fam-personality-traits",
    "Personality Trait",
    "e.g. Loyal",
    "_selected_familiar_personality_trait",
    confirm_remove=False,  # STORY-1109 B6
)
_FAMILIAR_REPUTATIONS = _TraitList(
    "selected_familiar",
    "reputations",
    "section-fam-reputations",
    "Reputation",
    "e.g. Fierce Protector",
    "_selected_familiar_reputation",
    signed=False,
    confirm_remove=False,  # STORY-1109 B6
)
_COVENANT_REPUTATIONS = _TraitList(
    "selected_covenant",
    "reputations",
    "section-cov-reputations",
    "Reputation",
    "e.g. Feared by the local nobility",
    "_selected_reputation",
    prompt_options={
        "min_score": _COVENANT_REPUTATION_RANGE[0],
        "max_score": _COVENANT_REPUTATION_RANGE[1],
        "include_known": True,
    },
)

#: Which sheet section each covenant Boon/Hook kind lives in.
_BOON_HOOK_SECTION = {"Boon": "section-cov-boons", "Hook": "section-cov-hooks"}


def _sign_colored(value: float, text: str) -> str:
    """Wraps `text` in Textual markup coloured by the sign of `value`:
    zero is cyan, positive green, negative red."""
    colour = "cyan" if value == 0 else "green" if value > 0 else "red"
    return f"[{colour}]{text}[/]"


class ThemeBar(Static):
    """A one-line bar above the footer showing the app's active theme name."""

    DEFAULT_CSS = """
    ThemeBar {
        height: 1;
        content-align: left middle;
        padding: 0 1;
        color: $text-muted;
    }
    """

    def on_mount(self) -> None:
        self.watch(self.app, "theme", self._show_theme, init=True)

    def _show_theme(self, theme_name: str) -> None:
        self.update(f"Theme: {theme_name.replace('-', ' ').title()}")


class BottomBar(Vertical):
    """Docks the ThemeBar directly above the Footer.

    Both dock to the same screen edge independently otherwise (Textual's
    dock arrangement doesn't stack same-edge docked siblings -- they'd
    overlap on the same row), so this wraps them in one bottom-docked
    container where Footer's own `dock: bottom` pins it to the container's
    last row and ThemeBar, undocked, takes the row above it in normal flow.
    """

    DEFAULT_CSS = """
    BottomBar {
        dock: bottom;
        height: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield ThemeBar(id="theme-bar")
        yield Footer()


class SagaCreateScreen(ModalScreen[str | None]):
    """A form for creating a new saga. Dismisses with the new saga's id, or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    SagaCreateScreen {
        align: center middle;
    }

    #create-dialog {
        width: 64;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #create-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #create-year-row {
        width: 100%;
        height: auto;
    }

    #create-buttons {
        width: 100%;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="create-dialog"):
            yield Label("Create a New Saga", id="create-title")
            yield Label("Saga name")
            yield Input(placeholder="e.g. Dammerstein", id="input-name")
            yield Label("Storyguide name")
            yield Input(placeholder="e.g. Alex", id="input-storyguide")
            with Horizontal(id="create-year-row"):
                yield Input(value="1220", type="integer", id="input-year")
                yield Select(
                    [(season, season) for season in SEASONS],
                    value=SEASONS[0],
                    allow_blank=False,
                    id="select-season",
                )
            yield Label("Description (optional)")
            yield Input(
                placeholder="A one-line premise for the saga",
                id="input-description",
            )
            yield Static("", id="create-error")
            with Horizontal(id="create-buttons"):
                yield Button("Create", id="btn-create", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-create":
            self._try_create()

    def _try_create(self) -> None:
        error = self.query_one("#create-error", Static)

        name = self.query_one("#input-name", Input).value.strip()
        if not name:
            error.update("Saga name is required.")
            return

        storyguide = self.query_one("#input-storyguide", Input).value.strip()
        if not storyguide:
            error.update("Storyguide name is required.")
            return

        year_raw = self.query_one("#input-year", Input).value.strip()
        try:
            year = int(year_raw)
        except ValueError:
            error.update("Start year must be a whole number.")
            return

        season = self.query_one("#select-season", Select).value
        if not isinstance(season, str):
            error.update("Start season is required.")
            return

        description = self.query_one("#input-description", Input).value.strip()

        saga = Saga(
            id=storage.generate_saga_id(name),
            name=name,
            storyguide=storyguide,
            description=description,
            current_year=year,
            current_season=season,
        )
        storage.save_saga(saga)
        self.dismiss(saga.id)


class EditSagaScreen(ModalScreen[dict[str, object] | None]):
    """Edits the saga's own Name, Storyguide and Description.

    The calendar (current year/season) has its own Set Date screen, and
    isn't touched here. Dismisses with a dict of {"name", "storyguide",
    "description"}, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditSagaScreen {
        align: center middle;
    }

    #saga-edit-dialog {
        width: 64;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .sagaedit-row {
        width: 100%;
        height: 1;
    }

    .sagaedit-row Label {
        width: 16;
    }

    .sagaedit-row Input {
        width: 1fr;
    }

    #saga-edit-error {
        color: $error;
        height: auto;
    }

    #saga-edit-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, saga: Saga) -> None:
        super().__init__()
        self.saga = saga

    def compose(self) -> ComposeResult:
        saga = self.saga
        with Vertical(id="saga-edit-dialog"):
            yield Label("Edit Saga")
            with Horizontal(classes="sagaedit-row"):
                yield Label("Name")
                yield Input(value=saga.name, id="input-saga-name", compact=True)
            with Horizontal(classes="sagaedit-row"):
                yield Label("Storyguide")
                yield Input(
                    value=saga.storyguide, id="input-saga-storyguide", compact=True
                )
            yield Label("Description (optional)")
            yield Input(value=saga.description, id="input-saga-description")
            yield Static("", id="saga-edit-error")
            with Horizontal(id="saga-edit-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#saga-edit-error", Static)

        name = self.query_one("#input-saga-name", Input).value.strip()
        if not name:
            error.update("Saga name is required.")
            return

        storyguide = self.query_one("#input-saga-storyguide", Input).value.strip()
        if not storyguide:
            error.update("Storyguide name is required.")
            return

        description = self.query_one("#input-saga-description", Input).value.strip()
        self.dismiss(
            {"name": name, "storyguide": storyguide, "description": description}
        )


class CovenantCreateScreen(ModalScreen[str | None]):
    """Creates a covenant within a saga.

    Dismisses with the new covenant's id, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    CovenantCreateScreen {
        align: center middle;
    }

    #create-dialog {
        width: 64;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #create-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #create-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, saga: Saga) -> None:
        super().__init__()
        self.saga = saga

    def compose(self) -> ComposeResult:
        with Vertical(id="create-dialog"):
            yield Label("Create a New Covenant", id="create-title")
            yield Label("Covenant name")
            yield Input(placeholder="e.g. Fengheld", id="input-name")
            yield Label("Notes (optional)")
            yield Input(
                placeholder="A one-line note about the covenant", id="input-notes"
            )
            yield Static("", id="create-error")
            with Horizontal(id="create-buttons"):
                yield Button("Create", id="btn-create", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-create":
            self._try_create()

    def _try_create(self) -> None:
        error = self.query_one("#create-error", Static)

        name = self.query_one("#input-name", Input).value.strip()
        if not name:
            error.update("Covenant name is required.")
            return

        notes = self.query_one("#input-notes", Input).value.strip()

        covenant_id = storage.generate_unique_id(
            name, [c.id for c in self.saga.covenants]
        )
        covenant = Covenant(
            id=covenant_id, saga_id=self.saga.id, name=name, notes=notes
        )
        self.saga.covenants.append(covenant)
        storage.save_saga(self.saga)
        self.dismiss(covenant_id)


class CharacterCreateScreen(ModalScreen[str | None]):
    """Creates a bare character: name, type, and covenant.

    Abilities, Virtues/Flaws, Arts, and lab assignment are left for later
    edit actions -- see DESIGN.md's Phase 1 forms slices. Dismisses with
    the new character's id, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    CharacterCreateScreen {
        align: center middle;
    }

    #create-dialog {
        width: 64;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #create-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #create-buttons {
        width: 100%;
        height: auto;
    }
    """

    _CHARACTER_TYPES: ClassVar[list[tuple[str, str]]] = [
        ("Magus", "magus"),
        ("Companion", "companion"),
        ("Grog", "grog"),
    ]

    def __init__(self, saga: Saga, default_covenant_id: str | None = None) -> None:
        super().__init__()
        self.saga = saga
        self.default_covenant_id = default_covenant_id

    def compose(self) -> ComposeResult:
        with Vertical(id="create-dialog"):
            yield Label("Create a New Character", id="create-title")
            yield Label("Character name")
            yield Input(placeholder="e.g. Leandro", id="input-name")
            yield Label("Type")
            yield Select(
                self._CHARACTER_TYPES,
                value="magus",
                allow_blank=False,
                id="select-type",
            )
            yield Label("Covenant (optional)")
            yield Select(
                [(escape(c.name), c.id) for c in self.saga.covenants],
                value=self.default_covenant_id or Select.NULL,
                allow_blank=True,
                prompt="(no covenant)",
                id="select-covenant",
            )
            yield Static("", id="create-error")
            with Horizontal(id="create-buttons"):
                yield Button("Create", id="btn-create", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-create":
            self._try_create()

    def _try_create(self) -> None:
        error = self.query_one("#create-error", Static)

        name = self.query_one("#input-name", Input).value.strip()
        if not name:
            error.update("Character name is required.")
            return

        character_type = self.query_one("#select-type", Select).value
        if not isinstance(character_type, str):
            error.update("Type is required.")
            return

        covenant_value = self.query_one("#select-covenant", Select).value
        covenant_id = covenant_value if isinstance(covenant_value, str) else None

        character = Character(
            id=storage.generate_unique_id(name, [c.id for c in self.saga.characters]),
            name=name,
            type=character_type,
            covenant_id=covenant_id,
        )
        self.saga.characters.append(character)
        storage.save_saga(self.saga)
        self.dismiss(character.id)


class ParamPromptScreen(ModalScreen[dict[str, str] | None]):
    """Prompts for a catalog entry's placeholder parameters.

    Generic over any catalog entry shape that has a `name` (shown as a
    title) and a list of `parameters` to fill in -- e.g. VirtueFlawDef's
    "Affinity with {art}" needing "art", or AbilityDef's "Craft: {craft}"
    needing "craft". Dismisses with a dict of param name -> value, or
    None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    ParamPromptScreen {
        align: center middle;
    }

    #param-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #param-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #param-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, prompt_title: str, parameters: list[str]) -> None:
        super().__init__()
        self.prompt_title = prompt_title
        self.parameters = parameters

    def compose(self) -> ComposeResult:
        with Vertical(id="param-dialog"):
            yield Label(self.prompt_title, id="param-title")
            for param in self.parameters:
                yield Label(param.title())
                yield Input(placeholder="e.g. Creo", id=f"input-param-{param}")
            yield Static("", id="param-error")
            with Horizontal(id="param-buttons"):
                yield Button("Confirm", id="btn-confirm", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-confirm":
            self._try_confirm()

    def _try_confirm(self) -> None:
        error = self.query_one("#param-error", Static)
        params: dict[str, str] = {}
        for param in self.parameters:
            value = self.query_one(f"#input-param-{param}", Input).value.strip()
            if not value:
                error.update(f"{param.title()} is required.")
                return
            params[param] = value.lower()
        self.dismiss(params)


class SearchablePickerScreen(ModalScreen[Any]):
    """Base for a ListView-backed catalog picker with a live-filtering
    search box above it.

    The Ability and Virtue/Flaw catalogs are large (78 and 624 entries) --
    a flat unsearchable list doesn't scale, so every catalog picker shares this:
    an Input above the ListView that re-filters it on every keystroke.
    Subclasses supply the entry list and how to search/render/activate
    each one; this owns the Input<->ListView wiring, so that trickier bit
    (live rebuild, keeping the search box focused and typable while
    letting Down/Enter reach the list) only has to be gotten right once.

    Subclasses override: `PICKER_TITLE`, `EMPTY_MESSAGE`,
    `SEARCH_PLACEHOLDER`, `LIST_VIEW_ID` (kept distinct per picker, not
    shared, so existing tests that query e.g. "#vf-picker-list" by id
    keep working) and the `_load_entries`/`_search_text`/`_label_for`/
    `_item_id`/`_on_entry_selected` hooks below.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    PICKER_TITLE: ClassVar[str] = "Pick"
    EMPTY_MESSAGE: ClassVar[str] = "(nothing available)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search..."
    LIST_VIEW_ID: ClassVar[str] = "picker-list"

    DEFAULT_CSS = """
    SearchablePickerScreen {
        align: center middle;
    }

    #picker-dialog {
        width: 76;
        height: auto;
        max-height: 28;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #picker-search {
        margin-bottom: 1;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._entries: list[Any] = []
        self._by_item_id: dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-dialog"):
            yield Label(self.PICKER_TITLE, id="picker-title")
            yield Input(placeholder=self.SEARCH_PLACEHOLDER, id="picker-search")
            yield ListView(id=self.LIST_VIEW_ID)
            yield Button("Cancel", id="btn-cancel")

    async def on_mount(self) -> None:
        self._entries = self._load_entries()
        await self._render_list("")
        self.query_one("#picker-search", Input).focus()

    # -- subclass hooks --

    def _load_entries(self) -> list[Any]:
        raise NotImplementedError

    def _search_text(self, entry: Any) -> str:
        raise NotImplementedError

    def _label_for(self, entry: Any) -> str:
        raise NotImplementedError

    def _item_id(self, entry: Any) -> str:
        raise NotImplementedError

    def _on_entry_selected(self, entry: Any) -> None:
        raise NotImplementedError

    # -- filtering / list rendering --

    async def _render_list(self, query: str) -> None:
        list_view = self.query_one(f"#{self.LIST_VIEW_ID}", ListView)
        await list_view.clear()
        self._by_item_id = {}

        if not self._entries:
            await list_view.append(ListItem(Label(self.EMPTY_MESSAGE)))
            return

        needle = query.strip().lower()
        matches = (
            [e for e in self._entries if needle in self._search_text(e).lower()]
            if needle
            else self._entries
        )
        if not matches:
            await list_view.append(ListItem(Label(f"(no matches for {query!r})")))
            return

        for entry in matches:
            item_id = self._item_id(entry)
            self._by_item_id[item_id] = entry
            await list_view.append(ListItem(Label(self._label_for(entry)), id=item_id))
        list_view.index = 0

    async def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "picker-search":
            await self._render_list(event.value)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        # Enter in the search box activates the top (highlighted) match,
        # the same way arrowing down to it and pressing Enter would.
        if event.input.id != "picker-search":
            return
        list_view = self.query_one(f"#{self.LIST_VIEW_ID}", ListView)
        if list_view.index is None:
            return
        await self._activate(list_view.children[list_view.index])

    def on_key(self, event: Key) -> None:
        # Input has no "down" binding of its own, so it would otherwise
        # just bubble and do nothing -- forward it to move focus into the
        # (already-filtered) list, the natural next step after typing.
        if event.key != "down":
            return
        search = self.query_one("#picker-search", Input)
        if self.focused is not search:
            return
        list_view = self.query_one(f"#{self.LIST_VIEW_ID}", ListView)
        if list_view.children:
            list_view.focus()
            event.stop()

    # -- selection / dismissal --

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        await self._activate(event.item)

    async def _activate(self, item: ListItem) -> None:
        if item.id is None:
            return
        entry = self._by_item_id.get(item.id)
        if entry is None:
            return
        self._on_entry_selected(entry)


class VirtueFlawPickerScreen(SearchablePickerScreen):
    """Pick a character Virtue/Flaw from the catalog, prompting for
    parameters if needed. Dismisses with the new instance, or None if
    cancelled.

    Laboratories have their own, separate Virtue/Flaw catalog and picker
    -- see LabVirtueFlawPickerScreen -- since a lab's Virtues & Flaws
    (ArM5 Chapter 8) are a completely different list from a character's
    (Chapter 4), even though both use the same VirtueFlawInstance shape
    and Free/Minor/Major tiers.
    """

    PICKER_TITLE: ClassVar[str] = "Add a Virtue or Flaw"
    EMPTY_MESSAGE: ClassVar[str] = "(no more Virtues/Flaws available)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search Virtues & Flaws..."
    LIST_VIEW_ID: ClassVar[str] = "vf-picker-list"

    def __init__(self, exclude_ids: set[str] | None = None) -> None:
        super().__init__()
        self._exclude_ids = exclude_ids or set()

    def _load_entries(self) -> list[VirtueFlawDef]:
        return [
            entry
            for entry in catalog.load_virtue_flaw_catalog()
            if entry.id not in self._exclude_ids
        ]

    def _search_text(self, entry: VirtueFlawDef) -> str:
        return f"{entry.name} {entry.type} {entry.category} {entry.tier}"

    def _label_for(self, entry: VirtueFlawDef) -> str:
        needs = f"  (needs: {', '.join(entry.parameters)})" if entry.parameters else ""
        return f"{entry.name}  [{entry.type}, {entry.tier}, cost {entry.cost}]{needs}"

    def _item_id(self, entry: VirtueFlawDef) -> str:
        return f"{_VIRTUE_FLAW_ITEM_ID_PREFIX}{entry.id}"

    def _on_entry_selected(self, entry: VirtueFlawDef) -> None:
        if not entry.parameters:
            self.dismiss(VirtueFlawInstance(vf_id=entry.id))
            return

        def handle_params(params: dict[str, str] | None) -> None:
            if params is not None:
                self.dismiss(VirtueFlawInstance(vf_id=entry.id, params=params))

        self.app.push_screen(
            ParamPromptScreen(entry.name, entry.parameters), handle_params
        )


class LabVirtueFlawPickerScreen(SearchablePickerScreen):
    """Pick a Laboratory Virtue/Flaw from the lab catalog (ArM5 Chapter 8
    -- Structure/Outfittings/Supernatural). Dismisses with the new
    instance, or None if cancelled.

    No ParamPromptScreen branch -- unlike character Virtues/Flaws, lab
    entries are never templated. `repeatable` entries (asterisked in the
    book -- Feature*, Person*, etc.) aren't excluded just because one's
    already attached, the same way templated character entries aren't.
    """

    PICKER_TITLE: ClassVar[str] = "Add a Laboratory Virtue or Flaw"
    EMPTY_MESSAGE: ClassVar[str] = "(no more Virtues/Flaws available)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search Laboratory Virtues & Flaws..."
    LIST_VIEW_ID: ClassVar[str] = "lab-vf-picker-list"

    def __init__(self, exclude_ids: set[str] | None = None) -> None:
        super().__init__()
        self._exclude_ids = exclude_ids or set()

    def _load_entries(self) -> list[LabVirtueFlawDef]:
        return [
            entry
            for entry in catalog.load_lab_virtue_flaw_catalog()
            if entry.repeatable or entry.id not in self._exclude_ids
        ]

    def _search_text(self, entry: LabVirtueFlawDef) -> str:
        return f"{entry.name} {entry.type} {entry.category} {entry.tier}"

    def _label_for(self, entry: LabVirtueFlawDef) -> str:
        return f"{entry.name}  [{entry.type}, {entry.tier}, cost {entry.cost}]"

    def _item_id(self, entry: LabVirtueFlawDef) -> str:
        return f"{_LAB_VIRTUE_FLAW_ITEM_ID_PREFIX}{entry.id}"

    def _on_entry_selected(self, entry: LabVirtueFlawDef) -> None:
        self.dismiss(VirtueFlawInstance(vf_id=entry.id))


class CovenantBoonHookPickerScreen(SearchablePickerScreen):
    """Pick a covenant Boon or Hook (ArM5 Chapter 6) from the catalog, then
    optionally name what it applies to (which Edifice, which contested
    resource...). Dismisses with the new VirtueFlawInstance, or None if
    cancelled.

    One picker for either kind: `kind` is "Boon" or "Hook". Nothing is
    hidden or blocked: entries already attached are marked "(taken)" but
    can be taken again (a covenant may well have two Edifices), and
    prerequisites and exclusions are shown as notes only.
    """

    LIST_VIEW_ID: ClassVar[str] = "covbh-picker-list"

    def __init__(self, kind: str, attached_ids: list[str] | None = None) -> None:
        super().__init__()
        self.kind = kind
        self._taken = Counter(attached_ids or [])
        self._by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        self.PICKER_TITLE = f"Add a {kind}"
        self.EMPTY_MESSAGE = f"(no more {kind}s available)"
        self.SEARCH_PLACEHOLDER = f"Search {kind}s..."

    def _load_entries(self) -> list[CovenantBoonHookDef]:
        return sorted(
            (entry for entry in self._by_id.values() if entry.type == self.kind),
            key=catalog.boon_hook_sort_key,
        )

    def _search_text(self, entry: CovenantBoonHookDef) -> str:
        return f"{entry.name} {entry.category} {entry.tier} {entry.description}"

    def _names(self, ids: list[str]) -> str:
        return _boon_hook_names(ids, self._by_id)

    def _label_for(self, entry: CovenantBoonHookDef) -> str:
        facts = [entry.category] if entry.category else []
        facts.append(entry.tier)
        if entry.cost:
            facts.append(f"{abs(entry.cost):g} pt")
        label = f"{entry.name}  [{', '.join(facts)}]"
        if entry.requires:
            label += f"  (requires: {self._names(entry.requires)})"
        if entry.excludes:
            label += f"  (not with: {self._names(entry.excludes)})"
        if self._taken[entry.id]:
            label += f"  (taken x{self._taken[entry.id]})"
        return label

    def _item_id(self, entry: CovenantBoonHookDef) -> str:
        return f"{_COVENANT_BOON_HOOK_ITEM_ID_PREFIX}{entry.id}"

    def _on_entry_selected(self, entry: CovenantBoonHookDef) -> None:
        def handle_detail(result: tuple[str, str] | None) -> None:
            if result is None:
                return  # cancelled: back to the picker
            detail, description = result
            self.dismiss(
                VirtueFlawInstance(
                    vf_id=entry.id, params=boon_hook_params(detail, description)
                )
            )

        self.app.push_screen(BoonHookDetailScreen(self.kind, entry.name), handle_detail)


class AbilityDetailsScreen(ModalScreen[Ability | None]):
    """Prompts for level/xp/specialty once an Ability's name+category are known.

    Used both to add a new Ability (existing=None) and to edit one already
    on the sheet (existing provided, prefilled). Dismisses with the
    finished Ability, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    AbilityDetailsScreen {
        align: center middle;
    }

    #details-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #details-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #details-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(
        self, name: str, category: str, existing: Ability | None = None
    ) -> None:
        super().__init__()
        self.ability_name = name
        self.category = category
        self.existing = existing

    def compose(self) -> ComposeResult:
        level = self.existing.level if self.existing else 0
        xp = self.existing.xp if self.existing else 0
        xp_to_next = self.existing.xp_to_next if self.existing else 0
        specialty = self.existing.specialty if self.existing else ""

        with Vertical(id="details-dialog"):
            yield Label(self.ability_name, id="details-title")
            yield Label("Level")
            yield Input(value=str(level), type="integer", id="input-level")
            yield Label("XP")
            yield Input(value=str(xp), type="integer", id="input-xp")
            yield Label("XP to next level")
            yield Input(value=str(xp_to_next), type="integer", id="input-xp-to-next")
            yield Label("Specialty (optional)")
            yield Input(
                value=specialty or "", placeholder="e.g. Swords", id="input-specialty"
            )
            yield Static("", id="details-error")
            with Horizontal(id="details-buttons"):
                yield Button("Confirm", id="btn-confirm", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-confirm":
            self._try_confirm()

    def _try_confirm(self) -> None:
        error = self.query_one("#details-error", Static)
        try:
            level = int(self.query_one("#input-level", Input).value.strip())
            xp = int(self.query_one("#input-xp", Input).value.strip())
            xp_to_next = int(self.query_one("#input-xp-to-next", Input).value.strip())
        except ValueError:
            error.update("Level, XP and XP to next level must be whole numbers.")
            return

        specialty = self.query_one("#input-specialty", Input).value.strip() or None
        self.dismiss(
            Ability(
                name=self.ability_name,
                category=self.category,
                level=level,
                xp=xp,
                xp_to_next=xp_to_next,
                specialty=specialty,
            )
        )


class AbilityPickerScreen(SearchablePickerScreen):
    """Pick an Ability from the catalog, resolve any parameter, set score/specialty.

    Non-templated entries already held are excluded (no point in a second
    "Athletics" row); templated entries ("Craft: {craft}") stay available
    since a character can hold several distinct instances of the same
    family. Dismisses with the new Ability, or None if cancelled.
    """

    PICKER_TITLE: ClassVar[str] = "Add an Ability"
    EMPTY_MESSAGE: ClassVar[str] = "(no more Abilities available)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search Abilities..."
    LIST_VIEW_ID: ClassVar[str] = "ability-picker-list"

    def __init__(self, exclude_names: set[str] | None = None) -> None:
        super().__init__()
        self._exclude_names = exclude_names or set()

    def _load_entries(self) -> list[AbilityDef]:
        return [
            entry
            for entry in catalog.load_ability_catalog()
            if entry.parameters or entry.name not in self._exclude_names
        ]

    def _search_text(self, entry: AbilityDef) -> str:
        return f"{entry.name} {entry.category}"

    def _label_for(self, entry: AbilityDef) -> str:
        needs = f"  (needs: {', '.join(entry.parameters)})" if entry.parameters else ""
        return f"{entry.name}  [{entry.category}]{needs}"

    def _item_id(self, entry: AbilityDef) -> str:
        return f"{_ABILITY_ITEM_ID_PREFIX}{entry.id}"

    def _on_entry_selected(self, entry: AbilityDef) -> None:
        if entry.parameters:

            def handle_params(params: dict[str, str] | None) -> None:
                if params is not None:
                    self._prompt_details(
                        catalog.resolve_ability_name(entry, params), entry.category
                    )

            self.app.push_screen(
                ParamPromptScreen(entry.name, entry.parameters), handle_params
            )
        else:
            self._prompt_details(entry.name, entry.category)

    def _prompt_details(self, name: str, category: str) -> None:
        def handle_ability(ability: Ability | None) -> None:
            if ability is not None:
                self.dismiss(ability)

        self.app.push_screen(AbilityDetailsScreen(name, category), handle_ability)


class SpellChooserScreen(SearchablePickerScreen):
    """Pick a spell -- for a Lab Text or Casting Tablet, or a spell a magus
    knows: every spell there is (the catalog, the saga's own, any magus's
    invented spells) less any in `exclude`, searchable by name or shorthand.
    Dismisses with the spell id."""

    PICKER_TITLE: ClassVar[str] = "Choose the spell"
    EMPTY_MESSAGE: ClassVar[str] = "(no spells)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search spells by name or Arts (e.g. CrIg)..."
    LIST_VIEW_ID: ClassVar[str] = "spell-chooser-list"

    def __init__(
        self, saga: Saga, *, exclude: set[str] | None = None, title: str = ""
    ) -> None:
        super().__init__()
        self.saga = saga
        self.exclude = exclude or set()
        self.title_text = title or self.PICKER_TITLE
        self._origin: dict[str, str] = {}

    def on_mount(self) -> Any:
        self.query_one("#picker-title", Label).update(self.title_text)
        return super().on_mount()

    def _load_entries(self) -> list[Spell]:
        entries = []
        for spell, origin in spl.pickable_spells(self.saga):
            if spell.id in self.exclude:
                continue
            self._origin[spell.id] = origin
            entries.append(spell)
        return entries

    def _search_text(self, entry: Spell) -> str:
        return f"{entry.name} {spl.shorthand(entry)}"

    def _label_for(self, entry: Spell) -> str:
        return (
            f"{escape(entry.name)}  [dim]{escape(spl.shorthand(entry))}  "
            f"{escape(self._origin.get(entry.id, ''))}[/]"
        )

    def _item_id(self, entry: Spell) -> str:
        return f"spellpick-{entry.id}"

    def _on_entry_selected(self, entry: Spell) -> None:
        self.dismiss(entry.id)


class RemovalPickerScreen(ModalScreen[int | None]):
    """Pick one entry from a list of display labels, by index.

    Despite the name it's the generic "which one?" picker: used to choose
    what to remove, edit, restore or improve. The caller supplies the labels
    and acts on its own list using the returned index. Dismisses with that
    index, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    RemovalPickerScreen {
        align: center middle;
    }

    #picker-dialog {
        width: 76;
        height: auto;
        max-height: 24;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }
    """

    def __init__(self, title: str, labels: list[str]) -> None:
        super().__init__()
        self.prompt_title = title
        self.labels = labels

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-dialog"):
            yield Label(self.prompt_title, id="picker-title")
            yield ListView(id="removal-picker-list")
            yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        list_view = self.query_one("#removal-picker-list", ListView)
        if not self.labels:
            list_view.append(ListItem(Label("(nothing to remove)")))
            return

        for index, label in enumerate(self.labels):
            list_view.append(
                ListItem(Label(label), id=f"{_REMOVAL_ITEM_ID_PREFIX}{index}")
            )
        list_view.index = 0

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id is None or not item_id.startswith(_REMOVAL_ITEM_ID_PREFIX):
            return
        index = int(item_id.removeprefix(_REMOVAL_ITEM_ID_PREFIX))
        self.dismiss(index)


class EditArtsScreen(ModalScreen[dict[str, ArtScore] | None]):
    """Edits all 15 Hermetic Arts at once -- a fixed grid, not an addable
    list. Two side-by-side columns (Techniques, Forms), mirroring the sheet's
    own two-column Magical Arts display -- sized to fit every row without a
    scrollbar (Forms, the taller column, is only 10 rows). Each Art shows a
    Level / XP pair. Dismisses with a dict of every art's lowercase name ->
    ArtScore, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditArtsScreen {
        align: center middle;
    }

    #arts-dialog {
        width: auto;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
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
        margin-bottom: 1;
    }

    .art-row {
        width: auto;
        height: auto;
    }

    .art-row Label {
        width: 14;
        content-align: right middle;
        padding-right: 1;
    }

    .art-row .art-sep {
        width: 1;
        content-align: center middle;
    }

    .art-row Input {
        width: 5;
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

    def __init__(self, arts: dict[str, ArtScore]) -> None:
        super().__init__()
        self.arts = arts

    def compose(self) -> ComposeResult:
        def row(art_name: str):
            key = art_name.lower()
            score = self.arts.get(key, ArtScore())
            yield Label(f"{art_name} ({ART_ABBREVIATIONS[art_name]})")
            yield Input(
                value=str(score.level),
                type="integer",
                id=f"input-art-{key}-level",
                compact=True,
            )
            yield Label("/", classes="art-sep")
            yield Input(
                value=str(score.xp),
                type="integer",
                id=f"input-art-{key}-xp",
                compact=True,
            )

        with Vertical(id="arts-dialog"):
            yield Label("Edit Arts", id="arts-title")
            yield Label("Each score is Level / XP", id="arts-subtitle")
            with Horizontal(id="arts-columns"):
                with Vertical(id="arts-techniques-col"):
                    yield Label("Techniques", classes="column-heading")
                    for technique in TECHNIQUES:
                        with Horizontal(classes="art-row"):
                            yield from row(technique)
                with Vertical(id="arts-forms-col"):
                    yield Label("Forms", classes="column-heading")
                    for form in FORMS:
                        with Horizontal(classes="art-row"):
                            yield from row(form)
            yield Static("", id="arts-error")
            with Horizontal(id="arts-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#arts-error", Static)
        result: dict[str, ArtScore] = {}
        for art_name in ARTS:
            key = art_name.lower()
            level_raw = self.query_one(f"#input-art-{key}-level", Input).value.strip()
            xp_raw = self.query_one(f"#input-art-{key}-xp", Input).value.strip()
            try:
                level = int(level_raw)
                xp = int(xp_raw)
            except ValueError:
                error.update(f"{art_name} needs whole numbers for Level and XP.")
                return
            result[key] = ArtScore(level=level, xp=xp)
        self.dismiss(result)


class LaboratoryCreateScreen(ModalScreen[str | None]):
    """Creates a bare laboratory within a covenant.

    Owner assignment and Features are left for later edit actions, same
    reasoning as Character creation leaving lab assignment for later.
    Dismisses with the new laboratory's id, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    LaboratoryCreateScreen {
        align: center middle;
    }

    #create-dialog {
        width: 64;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #create-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #create-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, saga: Saga, covenant: Covenant | None = None) -> None:
        super().__init__()
        self.saga = saga
        self.covenant = covenant

    def compose(self) -> ComposeResult:
        with Vertical(id="create-dialog"):
            yield Label("Create a New Laboratory", id="create-title")
            yield Label("Laboratory name")
            yield Input(placeholder="e.g. The Alchemical Tower", id="input-name")
            yield Label("Size")
            yield Input(value="0", type="integer", id="input-size")
            yield Label("Covenant (optional)")
            yield Select(
                [(escape(c.name), c.id) for c in self.saga.covenants],
                value=self.covenant.id if self.covenant else Select.NULL,
                allow_blank=True,
                prompt="(no covenant)",
                id="select-covenant",
            )
            yield Static("", id="create-error")
            with Horizontal(id="create-buttons"):
                yield Button("Create", id="btn-create", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-create":
            self._try_create()

    def _try_create(self) -> None:
        error = self.query_one("#create-error", Static)

        name = self.query_one("#input-name", Input).value.strip()
        if not name:
            error.update("Laboratory name is required.")
            return

        try:
            size = int(self.query_one("#input-size", Input).value.strip())
        except ValueError:
            error.update("Size must be a whole number.")
            return

        covenant_value = self.query_one("#select-covenant", Select).value
        covenant_id = covenant_value if isinstance(covenant_value, str) else None

        laboratory = Laboratory(
            id=storage.generate_unique_id(
                name, [lab.id for lab in self.saga.laboratories]
            ),
            covenant_id=covenant_id,
            name=name,
            characteristics=LabCharacteristics(size=size),
        )
        self.saga.laboratories.append(laboratory)
        storage.save_saga(self.saga)
        self.dismiss(laboratory.id)


class FamiliarCreateScreen(ModalScreen[str | None]):
    """Binds a new Familiar to a magus (see reference/familiar-rules-and-
    sheet.md). Minimal fields only -- Name and which magus; everything else
    (Cords, binding details, etc.) is filled in via the Familiar sheet's Edit
    actions afterward, same "create minimal, edit the rest" pattern as every
    other create screen.

    True Friend (Virtue) and Loyal (Partner) +3 (Personality Trait) are
    granted automatically to both the familiar and its magus -- not left for
    the user to type in (see kanban STORY-206).

    Dismisses with the new familiar's id, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    FamiliarCreateScreen {
        align: center middle;
    }

    #create-dialog {
        width: 64;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #create-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #create-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, saga: Saga, default_magus_id: str | None = None) -> None:
        super().__init__()
        self.saga = saga
        self.default_magus_id = default_magus_id

    def compose(self) -> ComposeResult:
        magi = fam.unbonded_magi(self.saga)
        with Vertical(id="create-dialog"):
            yield Label("Bind a New Familiar", id="create-title")
            yield Label("Familiar name")
            yield Input(placeholder="e.g. Ashwing", id="input-name")
            yield Label("Magus Partner")
            yield Select(
                [(escape(c.name), c.id) for c in magi],
                value=self.default_magus_id
                if self.default_magus_id in {c.id for c in magi}
                else Select.NULL,
                allow_blank=True,
                prompt="(choose a magus)",
                id="select-magus",
            )
            yield Static("", id="create-error")
            with Horizontal(id="create-buttons"):
                yield Button("Create", id="btn-create", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-create":
            self._try_create()

    def _try_create(self) -> None:
        error = self.query_one("#create-error", Static)

        name = self.query_one("#input-name", Input).value.strip()
        if not name:
            error.update("Familiar name is required.")
            return

        magus_id = self.query_one("#select-magus", Select).value
        magus = self.saga.character(magus_id) if isinstance(magus_id, str) else None
        if magus is None:
            error.update("A Magus Partner is required.")
            return

        familiar = fam.bind_familiar(self.saga, magus, name)
        storage.save_saga(self.saga)
        self.dismiss(familiar.id)


class EditCharacterInfoScreen(ModalScreen[dict[str, object] | None]):
    """Edits the character sheet's top-panel info: Name, Covenant, Assigned
    Laboratory (magi only), Setting, Confidence, and Size. Type, Age,
    Current Year and Current Season are derived/fixed and aren't editable
    here. Dismisses with a dict of field values, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditCharacterInfoScreen {
        align: center middle;
    }

    #charinfo-dialog {
        width: 64;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .charinfo-row {
        width: 100%;
        height: 1;
    }

    .charinfo-row Label {
        width: 20;
    }

    .charinfo-row Input, .charinfo-row Select {
        width: 1fr;
    }

    #charinfo-error {
        color: $error;
        height: auto;
    }

    #charinfo-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, saga: Saga, character: Character) -> None:
        super().__init__()
        self.saga = saga
        self.character = character

    def compose(self) -> ComposeResult:
        character = self.character
        b = character.background
        with Vertical(id="charinfo-dialog"):
            yield Label("Edit Character Info")
            with Horizontal(classes="charinfo-row"):
                yield Label("Name")
                yield Input(
                    value=character.name, id="input-charinfo-name", compact=True
                )
            with Horizontal(classes="charinfo-row"):
                yield Label("Covenant")
                yield Select(
                    [(escape(c.name), c.id) for c in self.saga.covenants],
                    value=character.covenant_id or Select.NULL,
                    allow_blank=True,
                    prompt="(unassigned)",
                    id="select-charinfo-covenant",
                    compact=True,
                )
            if character.type == "magus":
                with Horizontal(classes="charinfo-row"):
                    yield Label("Assigned Laboratory")
                    yield Select(
                        [(escape(lab.name), lab.id) for lab in self.saga.laboratories],
                        value=character.assigned_lab_id or Select.NULL,
                        allow_blank=True,
                        prompt="(unassigned)",
                        id="select-charinfo-laboratory",
                        compact=True,
                    )
            with Horizontal(classes="charinfo-row"):
                yield Label("Setting")
                yield Input(value=b.setting, id="input-charinfo-setting", compact=True)
            with Horizontal(classes="charinfo-row"):
                yield Label("Confidence Score")
                yield Input(
                    value=str(b.confidence_score),
                    type="integer",
                    id="input-charinfo-confidence_score",
                    compact=True,
                )
            with Horizontal(classes="charinfo-row"):
                yield Label("Confidence Points")
                yield Input(
                    value=str(b.confidence_points),
                    type="integer",
                    id="input-charinfo-confidence_points",
                    compact=True,
                )
            with Horizontal(classes="charinfo-row"):
                yield Label("Size")
                yield Input(
                    value=str(b.size),
                    type="integer",
                    id="input-charinfo-size",
                    compact=True,
                )
            yield Static("", id="charinfo-error")
            with Horizontal(id="charinfo-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#charinfo-error", Static)

        name = self.query_one("#input-charinfo-name", Input).value.strip()
        if not name:
            error.update("Name is required.")
            return

        covenant_value = self.query_one("#select-charinfo-covenant", Select).value
        covenant_id = covenant_value if isinstance(covenant_value, str) else None

        laboratory_id: str | None = None
        if self.character.type == "magus":
            lab_value = self.query_one("#select-charinfo-laboratory", Select).value
            laboratory_id = lab_value if isinstance(lab_value, str) else None

        result: dict[str, object] = {
            "name": name,
            "covenant_id": covenant_id,
            "laboratory_id": laboratory_id,
            "setting": self.query_one("#input-charinfo-setting", Input).value.strip(),
        }

        for label, field_name in (
            ("Confidence Score", "confidence_score"),
            ("Confidence Points", "confidence_points"),
            ("Size", "size"),
        ):
            raw = self.query_one(f"#input-charinfo-{field_name}", Input).value.strip()
            try:
                result[field_name] = int(raw)
            except ValueError:
                error.update(f"{label} must be a whole number.")
                return

        self.dismiss(result)


class EditCharacteristicsScreen(ModalScreen[Characteristics | None]):
    """Edits all 8 Characteristics at once: Int/Per/Str/Sta, Pre/Com/Dex/Qik.

    Dismisses with the finished Characteristics, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditCharacteristicsScreen {
        align: center middle;
    }

    #char-dialog {
        width: 50;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .char-row {
        width: 100%;
        height: 1;
    }

    .char-row Label {
        width: 5;
    }

    .char-row Input {
        width: 1fr;
        margin-right: 2;
    }

    #char-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #char-buttons {
        width: 100%;
        height: auto;
    }
    """

    _ROW1: ClassVar[list[tuple[str, str]]] = [
        ("Int", "intelligence"),
        ("Per", "perception"),
        ("Str", "strength"),
        ("Sta", "stamina"),
    ]
    _ROW2: ClassVar[list[tuple[str, str]]] = [
        ("Pre", "presence"),
        ("Com", "communication"),
        ("Dex", "dexterity"),
        ("Qik", "quickness"),
    ]

    def __init__(self, characteristics: Characteristics) -> None:
        super().__init__()
        self.characteristics = characteristics

    def compose(self) -> ComposeResult:
        with Vertical(id="char-dialog"):
            yield Label("Edit Characteristics", id="char-title")
            for row in (self._ROW1, self._ROW2):
                with Horizontal(classes="char-row"):
                    for label, field_name in row:
                        yield Label(label)
                        yield Input(
                            value=str(getattr(self.characteristics, field_name)),
                            type="integer",
                            id=f"input-char-{field_name}",
                            compact=True,
                        )
            yield Static("", id="char-error")
            with Horizontal(id="char-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#char-error", Static)
        values: dict[str, int] = {}
        for label, field_name in (*self._ROW1, *self._ROW2):
            raw = self.query_one(f"#input-char-{field_name}", Input).value.strip()
            try:
                values[field_name] = int(raw)
            except ValueError:
                error.update(f"{label} must be a whole number.")
                return
        self.dismiss(Characteristics(**values))


class ItemAddScreen(ModalScreen[str | None]):
    """Freeform text entry for one line of text -- today, a laboratory
    Specialty or Feature.

    Dismisses with the item description, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    ItemAddScreen {
        align: center middle;
    }

    #create-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #create-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #create-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, title: str = "Add an Item", existing: str | None = None) -> None:
        super().__init__()
        self.title_text = title
        self.existing = existing

    def compose(self) -> ComposeResult:
        with Vertical(id="create-dialog"):
            yield Label(self.title_text, id="create-title")
            yield Input(
                value=self.existing or "",
                placeholder="e.g. Fine wool cloak",
                id="input-item",
            )
            yield Static("", id="create-error")
            with Horizontal(id="create-buttons"):
                yield Button(
                    "Add" if self.existing is None else "Save",
                    id="btn-create",
                    variant="success",
                )
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-create":
            self._try_create()

    def _try_create(self) -> None:
        error = self.query_one("#create-error", Static)
        item = self.query_one("#input-item", Input).value.strip()
        if not item:
            error.update("Item description is required.")
            return
        self.dismiss(item)


class ScoredTraitPromptScreen(ModalScreen[ScoredTrait | None]):
    """Name + integer score prompt, reused for Personality Traits and
    Reputations -- both are just a label and a score on the character
    sheet. Dismisses with a ScoredTrait, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    ScoredTraitPromptScreen {
        align: center middle;
    }

    #trait-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #trait-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #trait-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(
        self,
        title: str,
        name_placeholder: str,
        existing: ScoredTrait | None = None,
        *,
        min_score: int | None = None,
        max_score: int | None = None,
        include_known: bool = False,
    ) -> None:
        super().__init__()
        self.title_text = title
        self.name_placeholder = name_placeholder
        self.existing = existing
        #: Optional inclusive bounds (covenant Reputations are -3..+3).
        self.min_score = min_score
        self.max_score = max_score
        #: Covenant Reputations only: whether a bad Reputation the covenant
        #: doesn't know about should count against Loyalty -- see
        #: inhabitants.reputation_loyalty_penalty(). Character Personality
        #: Traits/Reputations never show this (always known=True).
        self.include_known = include_known

    def _score_label(self) -> str:
        if self.min_score is None or self.max_score is None:
            return "Score"
        return f"Score ({self.min_score:+d} to {self.max_score:+d})"

    def compose(self) -> ComposeResult:
        with Vertical(id="trait-dialog"):
            yield Label(self.title_text, id="trait-title")
            yield Label("Name")
            yield Input(
                value=self.existing.name if self.existing else "",
                placeholder=self.name_placeholder,
                id="input-trait-name",
            )
            yield Label(self._score_label())
            yield Input(
                value=str(self.existing.score) if self.existing else "0",
                type="integer",
                id="input-trait-score",
            )
            if self.include_known:
                yield Checkbox(
                    "Known by the covenant?",
                    value=self.existing.known if self.existing else True,
                    id="input-trait-known",
                )
            yield Static("", id="trait-error")
            with Horizontal(id="trait-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#trait-error", Static)
        name = self.query_one("#input-trait-name", Input).value.strip()
        if not name:
            error.update("Name is required.")
            return
        raw_score = self.query_one("#input-trait-score", Input).value.strip()
        try:
            score = int(raw_score)
        except ValueError:
            error.update("Score must be a whole number.")
            return
        if (self.min_score is not None and score < self.min_score) or (
            self.max_score is not None and score > self.max_score
        ):
            error.update(f"Score must be between {self._score_label()[6:-1]}.")
            return
        known = (
            self.query_one("#input-trait-known", Checkbox).value
            if self.include_known
            else True
        )
        self.dismiss(ScoredTrait(name=name, score=score, known=known))


class MasteryAbilityPromptScreen(ModalScreen[MasteryAbility | None]):
    """Name/Level/XP prompt for one Mastery Ability (Fast Casting,
    Penetration, ...). Dismisses with the finished MasteryAbility, or None
    if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    MasteryAbilityPromptScreen {
        align: center middle;
    }

    #mastery-ability-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #mastery-ability-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #mastery-ability-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, title: str, existing: MasteryAbility | None = None) -> None:
        super().__init__()
        self.title_text = title
        self.existing = existing

    def compose(self) -> ComposeResult:
        with Vertical(id="mastery-ability-dialog"):
            yield Label(self.title_text, id="mastery-ability-title")
            yield Label("Name")
            yield Input(
                value=self.existing.name if self.existing else "",
                placeholder="e.g. Fast Casting",
                id="input-mastery-ability-name",
            )
            yield Label("Level")
            yield Input(
                value=str(self.existing.level) if self.existing else "0",
                type="integer",
                id="input-mastery-ability-level",
            )
            yield Label("XP")
            yield Input(
                value=str(self.existing.xp) if self.existing else "0",
                type="integer",
                id="input-mastery-ability-xp",
            )
            yield Static("", id="mastery-ability-error")
            with Horizontal(id="mastery-ability-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#mastery-ability-error", Static)
        name = self.query_one("#input-mastery-ability-name", Input).value.strip()
        if not name:
            error.update("Name is required.")
            return
        try:
            level = int(self.query_one("#input-mastery-ability-level", Input).value)
            xp = int(self.query_one("#input-mastery-ability-xp", Input).value)
        except ValueError:
            error.update("Level and XP must be whole numbers.")
            return
        self.dismiss(MasteryAbility(name=name, level=level, xp=xp))


class MasteryEditScreen(ModalScreen[KnownSpell | None]):
    """Edits a known spell's Mastery: score, xp, and its Mastery Abilities
    (each with its own name/level/xp -- see MasteryAbility). Abilities are
    added/removed here and only committed to the character on Save.
    Dismisses with the finished KnownSpell, or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    MasteryEditScreen {
        align: center middle;
    }

    #mastery-dialog {
        width: 70;
        height: auto;
        max-height: 30;
        border: round $accent;
        padding: 1 2;
        background: $surface;
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
        with Vertical(id="mastery-dialog"):
            yield Label(f"Mastery: {self.spell_name}", id="mastery-title")
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
                ListItem(Label(f"{ability.name} {ability.level}/{ability.xp}"))
            )

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
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
            MasteryAbilityPromptScreen("Add a Mastery Ability"), handle_result
        )

    def _remove_ability(self) -> None:
        if not self._abilities:
            return
        list_view = self.query_one("#mastery-abilities-list", ListView)
        index = list_view.index
        if index is not None and index < len(self._abilities):
            del self._abilities[index]
            self._render_abilities()

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


class RawVisPromptScreen(ModalScreen[tuple[str, int] | None]):
    """Prompts for an Art + a number of pawns, to add to a character's Raw
    Vis. Dismisses with (art, pawns), or None if cancelled. Adding an Art
    that's already held increases its existing pawn count -- see
    WorkspaceScreen._add_raw_vis().
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    RawVisPromptScreen {
        align: center middle;
    }

    #vis-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #vis-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #vis-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, existing: tuple[str, int] | None = None) -> None:
        super().__init__()
        self.existing = existing

    def compose(self) -> ComposeResult:
        existing = self.existing
        with Vertical(id="vis-dialog"):
            yield Label(
                "Add Raw Vis" if existing is None else "Edit Raw Vis", id="vis-title"
            )
            yield Label("Art")
            yield Select(
                [(art, art.lower()) for art in ARTS],
                value=existing[0] if existing else Select.NULL,
                id="select-vis-art",
            )
            yield Label("Pawns")
            yield Input(
                value="1" if existing is None else str(existing[1]),
                type="integer",
                id="input-vis-pawns",
            )
            yield Static("", id="vis-error")
            with Horizontal(id="vis-buttons"):
                yield Button(
                    "Add" if existing is None else "Save",
                    id="btn-create",
                    variant="success",
                )
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-create":
            self._try_create()

    def _try_create(self) -> None:
        error = self.query_one("#vis-error", Static)
        art = self.query_one("#select-vis-art", Select).value
        if not isinstance(art, str):
            error.update("Choose an Art.")
            return
        raw_pawns = self.query_one("#input-vis-pawns", Input).value.strip()
        try:
            pawns = int(raw_pawns)
        except ValueError:
            error.update("Pawns must be a whole number.")
            return
        self.dismiss((art, pawns))


class EditBiographicalDetailScreen(ModalScreen[dict[str, object] | None]):
    """Edits the Description tab's Biographical Detail section: the
    remaining Background fields (Setting/Confidence/Size live in the top
    panel's EditCharacterInfoScreen) plus every Description field,
    including the new free-text Biography. Dismisses with
    {"background": Background, "description": Description}, or None if
    cancelled -- one dialog edits two dataclasses at once, so the caller
    assigns each half back to character.background/character.description.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditBiographicalDetailScreen {
        align: center middle;
    }

    #biodetail-dialog {
        width: 92;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #biodetail-scroll {
        height: auto;
        max-height: 14;
    }

    #biodetail-columns {
        height: auto;
    }

    #biodetail-fields {
        width: 1fr;
        height: auto;
        margin-right: 2;
    }

    .biodetail-row {
        width: 100%;
        height: 1;
    }

    .biodetail-row Label {
        width: 22;
    }

    .biodetail-row Input, .biodetail-row Select {
        width: 1fr;
    }

    #biodetail-biography-col {
        width: 1fr;
        height: auto;
    }

    #biodetail-biography {
        height: 13;
    }

    #biodetail-error {
        color: $error;
        height: auto;
    }

    #biodetail-buttons {
        width: 100%;
        height: auto;
    }
    """

    _BACKGROUND_STR_FIELDS: ClassVar[list[tuple[str, str]]] = [
        ("Player", "player"),
        ("Birth Name", "birth_name"),
        ("Race/Nationality", "race_nationality"),
        ("Place of Origin", "place_of_origin"),
        ("Religion", "religion"),
        ("Title/Profession", "title_profession"),
    ]

    _HANDEDNESS_OPTIONS: ClassVar[list[tuple[str, str]]] = [
        ("Right", "right"),
        ("Left", "left"),
        ("Ambidextrous", "ambidextrous"),
    ]

    def __init__(self, background: Background, description: Description) -> None:
        super().__init__()
        self.background = background
        self.description = description

    def compose(self) -> ComposeResult:
        b, d = self.background, self.description
        with Vertical(id="biodetail-dialog"):
            yield Label("Edit Biographical Detail")
            with (
                VerticalScroll(id="biodetail-scroll"),
                Horizontal(id="biodetail-columns"),
            ):
                with Vertical(id="biodetail-fields"):
                    with Horizontal(classes="biodetail-row"):
                        yield Label("Player")
                        yield Input(value=b.player, id="input-bio-player", compact=True)
                    with Horizontal(classes="biodetail-row"):
                        yield Label("Birth Name")
                        yield Input(
                            value=b.birth_name,
                            id="input-bio-birth_name",
                            compact=True,
                        )
                    with Horizontal(classes="biodetail-row"):
                        yield Label("Year Born")
                        yield Input(
                            value="" if b.year_born is None else str(b.year_born),
                            type="integer",
                            id="input-bio-year_born",
                            compact=True,
                        )
                    with Horizontal(classes="biodetail-row"):
                        yield Label("Race/Nationality")
                        yield Input(
                            value=b.race_nationality,
                            id="input-bio-race_nationality",
                            compact=True,
                        )
                    with Horizontal(classes="biodetail-row"):
                        yield Label("Place of Origin")
                        yield Input(
                            value=b.place_of_origin,
                            id="input-bio-place_of_origin",
                            compact=True,
                        )
                    with Horizontal(classes="biodetail-row"):
                        yield Label("Religion")
                        yield Input(
                            value=b.religion, id="input-bio-religion", compact=True
                        )
                    with Horizontal(classes="biodetail-row"):
                        yield Label("Title/Profession")
                        yield Input(
                            value=b.title_profession,
                            id="input-bio-title_profession",
                            compact=True,
                        )
                    with Horizontal(classes="biodetail-row"):
                        yield Label("Height")
                        yield Input(
                            value="" if d.height is None else str(d.height),
                            id="input-bio-height",
                            compact=True,
                        )
                    with Horizontal(classes="biodetail-row"):
                        yield Label("Weight")
                        yield Input(
                            value="" if d.weight is None else str(d.weight),
                            id="input-bio-weight",
                            compact=True,
                        )
                    with Horizontal(classes="biodetail-row"):
                        yield Label("Hair")
                        yield Input(value=d.hair, id="input-bio-hair", compact=True)
                    with Horizontal(classes="biodetail-row"):
                        yield Label("Eyes")
                        yield Input(value=d.eyes, id="input-bio-eyes", compact=True)
                    with Horizontal(classes="biodetail-row"):
                        yield Label("Handedness")
                        yield Select(
                            self._HANDEDNESS_OPTIONS,
                            value=d.handedness,
                            allow_blank=False,
                            id="select-bio-handedness",
                            compact=True,
                        )
                    with Horizontal(classes="biodetail-row"):
                        yield Label("Physical Description")
                        yield Input(
                            value=d.physical_description,
                            id="input-bio-physical_description",
                            compact=True,
                        )
                with Vertical(id="biodetail-biography-col"):
                    yield Label("Biography")
                    yield TextArea(d.biography, id="biodetail-biography")
            yield Static("", id="biodetail-error")
            with Horizontal(id="biodetail-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#biodetail-error", Static)

        background_values: dict[str, object] = {
            # Not editable in this dialog -- seed through unchanged.
            "setting": self.background.setting,
            "confidence_score": self.background.confidence_score,
            "confidence_points": self.background.confidence_points,
            "size": self.background.size,
        }
        for _label, field_name in self._BACKGROUND_STR_FIELDS:
            background_values[field_name] = self.query_one(
                f"#input-bio-{field_name}", Input
            ).value.strip()

        raw_year_born = self.query_one("#input-bio-year_born", Input).value.strip()
        if raw_year_born:
            try:
                background_values["year_born"] = int(raw_year_born)
            except ValueError:
                error.update("Year Born must be a whole number.")
                return
        else:
            background_values["year_born"] = None

        height: float | None = None
        raw_height = self.query_one("#input-bio-height", Input).value.strip()
        if raw_height:
            try:
                height = float(raw_height)
            except ValueError:
                error.update("Height must be a number.")
                return

        weight: float | None = None
        raw_weight = self.query_one("#input-bio-weight", Input).value.strip()
        if raw_weight:
            try:
                weight = float(raw_weight)
            except ValueError:
                error.update("Weight must be a number.")
                return

        handedness = self.query_one("#select-bio-handedness", Select).value
        description = Description(
            height=height,
            weight=weight,
            hair=self.query_one("#input-bio-hair", Input).value.strip(),
            eyes=self.query_one("#input-bio-eyes", Input).value.strip(),
            handedness=handedness,  # type: ignore[arg-type]
            physical_description=self.query_one(
                "#input-bio-physical_description", Input
            ).value.strip(),
            biography=self.query_one("#biodetail-biography", TextArea).text.rstrip(),
        )

        self.dismiss(
            {"background": Background(**background_values), "description": description}
        )


class EditAgingScreen(ModalScreen[Aging | None]):
    """Edits Decrepitude and Warping (Score/Points, like an Ability's
    Level/XP -- see Aging's docstring). Dismisses with the finished Aging,
    or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditAgingScreen {
        align: center middle;
    }

    #aging-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .agingedit-row {
        width: 100%;
        height: 1;
    }

    .agingedit-row Label {
        width: 18;
    }

    .agingedit-row Input {
        width: 1fr;
    }

    #aging-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #aging-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, aging: Aging) -> None:
        super().__init__()
        self.aging = aging

    def compose(self) -> ComposeResult:
        a = self.aging
        with Vertical(id="aging-dialog"):
            yield Label("Edit Aging & Warping", id="aging-title")
            with Horizontal(classes="agingedit-row"):
                yield Label("Decrepitude")
                yield Input(
                    value=str(a.decrepitude),
                    type="integer",
                    id="input-aging-decrepitude",
                    compact=True,
                )
            with Horizontal(classes="agingedit-row"):
                yield Label("Effects of Aging")
                yield Input(value=a.effects, id="input-aging-effects", compact=True)
            with Horizontal(classes="agingedit-row"):
                yield Label("Warping Score")
                yield Input(
                    value=str(a.warping_score),
                    type="integer",
                    id="input-aging-warping_score",
                    compact=True,
                )
            with Horizontal(classes="agingedit-row"):
                yield Label("Warping Points")
                yield Input(
                    value=str(a.warping_points),
                    type="integer",
                    id="input-aging-warping_points",
                    compact=True,
                )
            yield Static("", id="aging-error")
            with Horizontal(id="aging-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#aging-error", Static)
        values: dict[str, object] = {}
        for label, field_name in (
            ("Decrepitude", "decrepitude"),
            ("Warping Score", "warping_score"),
            ("Warping Points", "warping_points"),
        ):
            raw = self.query_one(f"#input-aging-{field_name}", Input).value.strip()
            try:
                values[field_name] = int(raw)
            except ValueError:
                error.update(f"{label} must be a whole number.")
                return
        values["effects"] = self.query_one("#input-aging-effects", Input).value.strip()
        self.dismiss(Aging(**values))


class EditWoundsScreen(ModalScreen[Wounds | None]):
    """Edits Soak, Wound counts per severity, and Incapacitated/Dead. Simple
    counts, not individual wound records -- matches checking boxes on the
    paper sheet, not the calculated Wound Penalty (see Wounds's docstring).
    Dismisses with the finished Wounds, or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditWoundsScreen {
        align: center middle;
    }

    #wounds-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .woundsedit-row {
        width: 100%;
        height: 1;
    }

    .woundsedit-row Label {
        width: 22;
    }

    .woundsedit-row Input {
        width: 1fr;
    }

    #wounds-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #wounds-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, wounds: Wounds) -> None:
        super().__init__()
        self.wounds = wounds

    def compose(self) -> ComposeResult:
        w = self.wounds
        with Vertical(id="wounds-dialog"):
            yield Label("Edit Wounds", id="wounds-title")
            with Horizontal(classes="woundsedit-row"):
                yield Label("Soak")
                yield Input(
                    value=str(w.soak),
                    type="integer",
                    id="input-wounds-soak",
                    compact=True,
                )
            with Horizontal(classes="woundsedit-row"):
                yield Label("Light Wounds (-1 each)")
                yield Input(
                    value=str(w.light),
                    type="integer",
                    id="input-wounds-light",
                    compact=True,
                )
            with Horizontal(classes="woundsedit-row"):
                yield Label("Medium Wounds (-3 each)")
                yield Input(
                    value=str(w.medium),
                    type="integer",
                    id="input-wounds-medium",
                    compact=True,
                )
            with Horizontal(classes="woundsedit-row"):
                yield Label("Heavy Wounds (-5 each)")
                yield Input(
                    value=str(w.heavy),
                    type="integer",
                    id="input-wounds-heavy",
                    compact=True,
                )
            yield Checkbox(
                "Incapacitated",
                value=w.incapacitated,
                id="check-wounds-incapacitated",
                compact=True,
            )
            yield Checkbox("Dead", value=w.dead, id="check-wounds-dead", compact=True)
            yield Static("", id="wounds-error")
            with Horizontal(id="wounds-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#wounds-error", Static)
        values: dict[str, object] = {}
        for label, field_name in (
            ("Soak", "soak"),
            ("Light Wounds", "light"),
            ("Medium Wounds", "medium"),
            ("Heavy Wounds", "heavy"),
        ):
            raw = self.query_one(f"#input-wounds-{field_name}", Input).value.strip()
            try:
                values[field_name] = int(raw)
            except ValueError:
                error.update(f"{label} must be a whole number.")
                return
        values["incapacitated"] = self.query_one(
            "#check-wounds-incapacitated", Checkbox
        ).value
        values["dead"] = self.query_one("#check-wounds-dead", Checkbox).value
        self.dismiss(Wounds(**values))


class EditFatigueScreen(ModalScreen[FatigueLevel | None]):
    """Picks the character's current Fatigue Level. Dismisses with the
    chosen level, or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditFatigueScreen {
        align: center middle;
    }

    #fatigue-dialog {
        width: 50;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .fatigueedit-row {
        width: 100%;
        height: 1;
    }

    .fatigueedit-row Label {
        width: 14;
    }

    .fatigueedit-row Select {
        width: 1fr;
    }

    #fatigue-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, current: FatigueLevel) -> None:
        super().__init__()
        self.current = current

    def compose(self) -> ComposeResult:
        with Vertical(id="fatigue-dialog"):
            yield Label("Edit Fatigue Level", id="fatigue-title")
            with Horizontal(classes="fatigueedit-row"):
                yield Label("Level")
                yield Select(
                    [(level.title(), level) for level in FATIGUE_LEVELS],
                    value=self.current,
                    allow_blank=False,
                    id="select-fatigue-level",
                    compact=True,
                )
            with Horizontal(id="fatigue-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            level = self.query_one("#select-fatigue-level", Select).value
            self.dismiss(level)  # type: ignore[arg-type]


class EditHermeticBackgroundScreen(ModalScreen[HermeticBackground | None]):
    """Edits a magus's Hermetic lineage block: House (picked from the
    catalog) plus Domus Magna/Primus/Parens/Covenant of Apprenticeship/
    Wizard's Sigil. Dismisses with the finished HermeticBackground, or None
    if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditHermeticBackgroundScreen {
        align: center middle;
    }

    #hermetic-dialog {
        width: 70;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .hermeticedit-row {
        width: 100%;
        height: 1;
    }

    .hermeticedit-row Label {
        width: 26;
    }

    .hermeticedit-row Input, .hermeticedit-row Select {
        width: 1fr;
    }

    #hermetic-buttons {
        width: 100%;
        height: auto;
    }
    """

    _STR_FIELDS_BEFORE_AGE: ClassVar[list[tuple[str, str]]] = [
        ("Domus Magna", "domus_magna"),
        ("Primus", "primus"),
        ("Parens", "parens"),
        ("Covenant of Apprenticeship", "covenant_of_apprenticeship"),
    ]
    _STR_FIELDS_AFTER_AGE: ClassVar[list[tuple[str, str]]] = [
        ("Wizard's Sigil", "wizards_sigil"),
    ]

    def __init__(self, hermetic: HermeticBackground) -> None:
        super().__init__()
        self.hermetic = hermetic

    def compose(self) -> ComposeResult:
        h = self.hermetic
        houses = catalog.load_house_catalog()
        with Vertical(id="hermetic-dialog"):
            yield Label("Edit Hermetic Background", id="hermetic-title")
            with Horizontal(classes="hermeticedit-row"):
                yield Label("House")
                yield Select(
                    [(house.name, house.id) for house in houses],
                    value=h.house or Select.NULL,
                    allow_blank=True,
                    prompt="(none selected)",
                    id="select-hermetic-house",
                    compact=True,
                )
            for label, field_name in self._STR_FIELDS_BEFORE_AGE:
                with Horizontal(classes="hermeticedit-row"):
                    yield Label(label)
                    yield Input(
                        value=getattr(h, field_name),
                        id=f"input-hermetic-{field_name}",
                        compact=True,
                    )
            with Horizontal(classes="hermeticedit-row"):
                yield Label("Age of Apprenticeship")
                yield Input(
                    value=(
                        ""
                        if h.age_of_apprenticeship is None
                        else str(h.age_of_apprenticeship)
                    ),
                    type="integer",
                    id="input-hermetic-age_of_apprenticeship",
                    compact=True,
                )
            for label, field_name in self._STR_FIELDS_AFTER_AGE:
                with Horizontal(classes="hermeticedit-row"):
                    yield Label(label)
                    yield Input(
                        value=getattr(h, field_name),
                        id=f"input-hermetic-{field_name}",
                        compact=True,
                    )
            with Horizontal(id="hermetic-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            house_value = self.query_one("#select-hermetic-house", Select).value
            house = house_value if isinstance(house_value, str) else None
            values: dict[str, object] = {"house": house}
            for _label, field_name in (
                *self._STR_FIELDS_BEFORE_AGE,
                *self._STR_FIELDS_AFTER_AGE,
            ):
                values[field_name] = self.query_one(
                    f"#input-hermetic-{field_name}", Input
                ).value.strip()
            raw_age = self.query_one(
                "#input-hermetic-age_of_apprenticeship", Input
            ).value.strip()
            values["age_of_apprenticeship"] = int(raw_age) if raw_age else None
            self.dismiss(HermeticBackground(**values))


class EditLabIdentityScreen(ModalScreen[dict[str, object] | None]):
    """Edits a Laboratory's Name/Location/Build Points/Aura modifier, and (unlike
    character Identity editing) lets you reassign its Owner from the
    lab's own side. It only returns the chosen `owner_id`;
    models.assign_laboratory_owner() does the two-way sync.
    Dismisses with {"name", "location", "build_points", "aura_modifier",
    "covenant_id", "owner_id"}, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditLabIdentityScreen {
        align: center middle;
    }

    #lab-identity-dialog {
        width: 64;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .labid-row {
        width: 100%;
        height: 1;
    }

    .labid-row Label {
        width: 22;
    }

    .labid-row Input, .labid-row Select {
        width: 1fr;
    }

    #lab-identity-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #lab-identity-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, saga: Saga, laboratory: Laboratory) -> None:
        super().__init__()
        self.saga = saga
        self.laboratory = laboratory

    def compose(self) -> ComposeResult:
        lab = self.laboratory
        with Vertical(id="lab-identity-dialog"):
            yield Label("Edit Laboratory Identity", id="lab-identity-title")
            with Horizontal(classes="labid-row"):
                yield Label("Name")
                yield Input(value=lab.name, id="input-lab-name", compact=True)
            with Horizontal(classes="labid-row"):
                yield Label("Location")
                yield Input(value=lab.location, id="input-lab-location", compact=True)
            with Horizontal(classes="labid-row"):
                yield Label("Points (Build Points)")
                yield Input(
                    value=str(lab.build_points),
                    type="integer",
                    id="input-lab-points",
                    compact=True,
                )
            with Horizontal(classes="labid-row"):
                yield Label("Aura modifier")
                yield Input(
                    value=str(lab.aura_modifier),
                    type="integer",
                    id="input-lab-aura-modifier",
                    compact=True,
                )
            with Horizontal(classes="labid-row"):
                yield Label("Covenant")
                yield Select(
                    [(escape(c.name), c.id) for c in self.saga.covenants],
                    value=lab.covenant_id or Select.NULL,
                    allow_blank=True,
                    prompt="(unassigned)",
                    id="select-lab-covenant",
                    compact=True,
                )
            with Horizontal(classes="labid-row"):
                yield Label("Owner")
                yield Select(
                    [
                        (escape(c.name), c.id)
                        for c in self.saga.characters
                        if c.type == "magus"
                    ],
                    value=lab.owner_id or Select.NULL,
                    allow_blank=True,
                    prompt="(unassigned)",
                    id="select-lab-owner",
                    compact=True,
                )
            yield Static("", id="lab-identity-error")
            with Horizontal(id="lab-identity-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#lab-identity-error", Static)

        name = self.query_one("#input-lab-name", Input).value.strip()
        if not name:
            error.update("Name is required.")
            return

        raw_points = self.query_one("#input-lab-points", Input).value.strip()
        try:
            build_points = int(raw_points)
        except ValueError:
            error.update("Points must be a whole number.")
            return

        raw_aura = self.query_one("#input-lab-aura-modifier", Input).value.strip()
        try:
            aura_modifier = int(raw_aura)
        except ValueError:
            error.update("Aura modifier must be a whole number.")
            return

        owner_value = self.query_one("#select-lab-owner", Select).value
        owner_id = owner_value if isinstance(owner_value, str) else None

        covenant_value = self.query_one("#select-lab-covenant", Select).value
        covenant_id = covenant_value if isinstance(covenant_value, str) else None

        self.dismiss(
            {
                "name": name,
                "location": self.query_one("#input-lab-location", Input).value.strip(),
                "build_points": build_points,
                "aura_modifier": aura_modifier,
                "covenant_id": covenant_id,
                "owner_id": owner_id,
            }
        )


class EditLabCharacteristicsScreen(ModalScreen[LabCharacteristics | None]):
    """Edits the manual (base) component of the 8 Laboratory
    Characteristics -- see LabCharacteristics's docstring for why this is
    only the manual component, not the Virtue/Flaw-derived total.
    Dismisses with the finished LabCharacteristics, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditLabCharacteristicsScreen {
        align: center middle;
    }

    #lab-char-dialog {
        width: 64;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #lab-char-fields {
        height: auto;
        max-height: 14;
    }

    .labchar-row {
        width: 100%;
        height: 1;
    }

    .labchar-row Label {
        width: 18;
    }

    .labchar-row Input {
        width: 1fr;
    }

    #lab-char-buttons {
        width: 100%;
        height: auto;
    }

    #lab-char-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, characteristics: LabCharacteristics) -> None:
        super().__init__()
        self.characteristics = characteristics

    def compose(self) -> ComposeResult:
        # Fields scroll (if the terminal is very short); the buttons sit
        # outside the scroll region so Save/Cancel are always visible.
        with Vertical(id="lab-char-dialog"):
            yield Label("Edit Laboratory Characteristics (manual value)")
            with VerticalScroll(id="lab-char-fields"):
                for characteristic in LAB_CHARACTERISTICS:
                    with Horizontal(classes="labchar-row"):
                        yield Label(characteristic.replace("_", " ").title())
                        yield Input(
                            value=str(getattr(self.characteristics, characteristic)),
                            type="integer",
                            id=f"input-labchar-{characteristic}",
                            compact=True,
                        )
            yield Static("", id="lab-char-error")
            with Horizontal(id="lab-char-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#lab-char-error", Static)
        values: dict[str, int] = {}
        for characteristic in LAB_CHARACTERISTICS:
            raw = self.query_one(
                f"#input-labchar-{characteristic}", Input
            ).value.strip()
            try:
                values[characteristic] = int(raw)
            except ValueError:
                error.update(
                    f"{characteristic.replace('_', ' ').title()} must be "
                    "a whole number."
                )
                return
        self.dismiss(LabCharacteristics(**values))


class NamedDescriptionPromptScreen(ModalScreen[NamedDescription | None]):
    """Name + free-text description prompt, reused for a Laboratory's
    Rooms and its Inventory items. Dismisses with a NamedDescription, or
    None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    NamedDescriptionPromptScreen {
        align: center middle;
    }

    #named-desc-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #named-desc-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #named-desc-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(
        self,
        title: str,
        name_placeholder: str,
        existing: NamedDescription | None = None,
    ) -> None:
        super().__init__()
        self.title_text = title
        self.name_placeholder = name_placeholder
        self.existing = existing

    def compose(self) -> ComposeResult:
        existing = self.existing
        with Vertical(id="named-desc-dialog"):
            yield Label(self.title_text, id="named-desc-title")
            yield Label("Name")
            yield Input(
                value=existing.name if existing else "",
                placeholder=self.name_placeholder,
                id="input-named-desc-name",
            )
            yield Label("Description")
            yield Input(
                value=existing.description if existing else "",
                id="input-named-desc-description",
            )
            yield Static("", id="named-desc-error")
            with Horizontal(id="named-desc-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#named-desc-error", Static)
        name = self.query_one("#input-named-desc-name", Input).value.strip()
        if not name:
            error.update("Name is required.")
            return
        description = self.query_one(
            "#input-named-desc-description", Input
        ).value.strip()
        self.dismiss(NamedDescription(name=name, description=description))


class DiaryEntryPromptScreen(ModalScreen[DiaryEntry | None]):
    """Year/Season/Name/Details prompt for a Laboratory diary entry.
    Dismisses with a DiaryEntry, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    DiaryEntryPromptScreen {
        align: center middle;
    }

    #diary-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #diary-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #diary-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(
        self,
        default_year: int,
        existing: DiaryEntry | None = None,
        default_season: str = SEASONS[0],
    ) -> None:
        super().__init__()
        self.default_year = default_year
        self.default_season = default_season
        self.existing = existing

    def compose(self) -> ComposeResult:
        existing = self.existing
        with Vertical(id="diary-dialog"):
            yield Label(
                "Add a Diary Entry" if existing is None else "Edit a Diary Entry",
                id="diary-title",
            )
            yield Label("Year")
            yield Input(
                value=str(existing.year if existing else self.default_year),
                type="integer",
                id="input-diary-year",
            )
            yield Label("Season")
            yield Select(
                [(season, season) for season in SEASONS],
                value=existing.season if existing else self.default_season,
                allow_blank=False,
                id="select-diary-season",
            )
            yield Label("Name")
            yield Input(
                value=existing.name if existing else "",
                placeholder="e.g. Invented a spell",
                id="input-diary-name",
            )
            yield Label("Details")
            yield Input(
                value=existing.details if existing else "", id="input-diary-details"
            )
            yield Static("", id="diary-error")
            with Horizontal(id="diary-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#diary-error", Static)
        raw_year = self.query_one("#input-diary-year", Input).value.strip()
        try:
            year = int(raw_year)
        except ValueError:
            error.update("Year must be a whole number.")
            return
        name = self.query_one("#input-diary-name", Input).value.strip()
        if not name:
            error.update("Name is required.")
            return
        season = self.query_one("#select-diary-season", Select).value
        details = self.query_one("#input-diary-details", Input).value.strip()
        self.dismiss(DiaryEntry(year=year, season=season, name=name, details=details))


class EditFamiliarInfoScreen(ModalScreen[dict[str, object] | None]):
    """Edits a Familiar's Partnership & Core Metadata (everything but its
    Magus Partner, which is set once at creation and never changes).
    Dismisses with a dict of field values, or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditFamiliarInfoScreen {
        align: center middle;
    }

    #fam-info-dialog {
        width: 64;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .faminfoedit-row {
        width: 100%;
        height: 1;
    }

    .faminfoedit-row Label {
        width: 22;
    }

    .faminfoedit-row Input, .faminfoedit-row Select {
        width: 1fr;
    }

    #fam-info-error {
        color: $error;
        height: auto;
    }

    #fam-info-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, familiar: Familiar) -> None:
        super().__init__()
        self.familiar = familiar

    def compose(self) -> ComposeResult:
        f = self.familiar
        with Vertical(id="fam-info-dialog"):
            yield Label("Edit Familiar")
            with Horizontal(classes="faminfoedit-row"):
                yield Label("Name")
                yield Input(value=f.name, id="input-fam-name", compact=True)
            with Horizontal(classes="faminfoedit-row"):
                yield Label("Species / Description")
                yield Input(value=f.species, id="input-fam-species", compact=True)
            with Horizontal(classes="faminfoedit-row"):
                yield Label("Season Bound")
                yield Select(
                    [(s, s) for s in SEASONS],
                    value=f.season_bound or Select.NULL,
                    allow_blank=True,
                    prompt="(not set)",
                    id="select-fam-season",
                    compact=True,
                )
            with Horizontal(classes="faminfoedit-row"):
                yield Label("Year Bound")
                yield Input(
                    value="" if f.year_bound is None else str(f.year_bound),
                    type="integer",
                    id="input-fam-year",
                    compact=True,
                )
            with Horizontal(classes="faminfoedit-row"):
                yield Label("Magic Might Score")
                yield Input(
                    value=str(f.magic_might),
                    type="integer",
                    id="input-fam-might",
                    compact=True,
                )
            with Horizontal(classes="faminfoedit-row"):
                yield Label("Current Might Pool")
                yield Input(
                    value="" if f.might_pool is None else str(f.might_pool),
                    type="integer",
                    id="input-fam-might-pool",
                    compact=True,
                )
            with Horizontal(classes="faminfoedit-row"):
                yield Label("Size")
                yield Input(
                    value=str(f.size), type="integer", id="input-fam-size", compact=True
                )
            with Horizontal(classes="faminfoedit-row"):
                yield Label("Wound Multiplier")
                yield Input(
                    value=str(f.wound_multiplier),
                    type="integer",
                    id="input-fam-wound-mult",
                    compact=True,
                )
            yield Static("", id="fam-info-error")
            with Horizontal(id="fam-info-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#fam-info-error", Static)

        name = self.query_one("#input-fam-name", Input).value.strip()
        if not name:
            error.update("Name is required.")
            return

        season_value = self.query_one("#select-fam-season", Select).value
        result: dict[str, object] = {
            "name": name,
            "species": self.query_one("#input-fam-species", Input).value.strip(),
            "season_bound": season_value if isinstance(season_value, str) else "",
        }

        for field_name, label in (
            ("input-fam-year", "Year Bound"),
            ("input-fam-might-pool", "Current Might Pool"),
        ):
            raw = self.query_one(f"#{field_name}", Input).value.strip()
            key = "year_bound" if field_name == "input-fam-year" else "might_pool"
            try:
                result[key] = int(raw) if raw else None
            except ValueError:
                error.update(f"{label} must be a whole number.")
                return

        for field_name, key, label in (
            ("input-fam-might", "magic_might", "Magic Might Score"),
            ("input-fam-size", "size", "Size"),
            ("input-fam-wound-mult", "wound_multiplier", "Wound Multiplier"),
        ):
            raw = self.query_one(f"#{field_name}", Input).value.strip()
            try:
                result[key] = int(raw)
            except ValueError:
                error.update(f"{label} must be a whole number.")
                return

        self.dismiss(result)


class EditFamiliarBindingScreen(ModalScreen[dict[str, object] | None]):
    """Edits a Familiar's Initial Binding details and the three Cords.
    Dismisses with a dict of field values, or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditFamiliarBindingScreen {
        align: center middle;
    }

    #fam-binding-dialog {
        width: 70;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
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
        with Vertical(id="fam-binding-dialog"):
            yield Label("Edit Binding & Cords")
            with Horizontal(classes="fambindingedit-row"):
                yield Label("Binding Technique")
                yield Select(
                    [(t, t) for t in TECHNIQUES],
                    value=f.binding_technique or Select.NULL,
                    allow_blank=True,
                    prompt="(not set)",
                    id="select-fam-technique",
                    compact=True,
                )
            with Horizontal(classes="fambindingedit-row"):
                yield Label("Binding Form")
                yield Select(
                    [(x, x) for x in FORMS],
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

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
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


class EditFamiliarCharacteristicsScreen(ModalScreen[dict[str, object] | None]):
    """Edits a Familiar's 8 Characteristics plus its two derived-defense
    figures (Base Soak, Magic Resistance) -- both typed in, no formula
    computed (see Familiar.base_soak/magic_resistance). Dismisses with
    {"characteristics": Characteristics, "base_soak": int,
    "magic_resistance": int}, or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditFamiliarCharacteristicsScreen {
        align: center middle;
    }

    #fam-char-dialog {
        width: 64;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .famcharedit-row {
        width: 100%;
        height: 1;
    }

    .famcharedit-row Label {
        width: 22;
    }

    .famcharedit-row Input {
        width: 1fr;
    }

    #fam-char-error {
        color: $error;
        height: auto;
    }

    #fam-char-buttons {
        width: 100%;
        height: auto;
    }
    """

    _CHARACTERISTICS: ClassVar[list[tuple[str, str]]] = [
        ("Intelligence (Int)", "intelligence"),
        ("Perception (Per)", "perception"),
        ("Presence (Pre)", "presence"),
        ("Communication (Com)", "communication"),
        ("Strength (Str)", "strength"),
        ("Stamina (Sta)", "stamina"),
        ("Dexterity (Dex)", "dexterity"),
        ("Quickness (Qik)", "quickness"),
    ]

    def __init__(self, familiar: Familiar) -> None:
        super().__init__()
        self.familiar = familiar

    def compose(self) -> ComposeResult:
        c = self.familiar.characteristics
        with Vertical(id="fam-char-dialog"):
            yield Label("Edit Characteristics")
            for label, field_name in self._CHARACTERISTICS:
                with Horizontal(classes="famcharedit-row"):
                    yield Label(label)
                    yield Input(
                        value=str(getattr(c, field_name)),
                        type="integer",
                        id=f"input-famchar-{field_name}",
                        compact=True,
                    )
            with Horizontal(classes="famcharedit-row"):
                yield Label("Base Soak")
                yield Input(
                    value=str(self.familiar.base_soak),
                    type="integer",
                    id="input-famchar-base-soak",
                    compact=True,
                )
            with Horizontal(classes="famcharedit-row"):
                yield Label("Magic Resistance")
                yield Input(
                    value=str(self.familiar.magic_resistance),
                    type="integer",
                    id="input-famchar-magic-resistance",
                    compact=True,
                )
            yield Static("", id="fam-char-error")
            with Horizontal(id="fam-char-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#fam-char-error", Static)
        values: dict[str, int] = {}
        for label, field_name in self._CHARACTERISTICS:
            raw = self.query_one(f"#input-famchar-{field_name}", Input).value.strip()
            try:
                values[field_name] = int(raw)
            except ValueError:
                error.update(f"{label} must be a whole number.")
                return

        for field_name, key, label in (
            ("input-famchar-base-soak", "base_soak", "Base Soak"),
            (
                "input-famchar-magic-resistance",
                "magic_resistance",
                "Magic Resistance",
            ),
        ):
            raw = self.query_one(f"#{field_name}", Input).value.strip()
            try:
                values[key] = int(raw)
            except ValueError:
                error.update(f"{label} must be a whole number.")
                return

        self.dismiss(
            {
                "characteristics": Characteristics(
                    intelligence=values["intelligence"],
                    perception=values["perception"],
                    presence=values["presence"],
                    communication=values["communication"],
                    strength=values["strength"],
                    stamina=values["stamina"],
                    dexterity=values["dexterity"],
                    quickness=values["quickness"],
                ),
                "base_soak": values["base_soak"],
                "magic_resistance": values["magic_resistance"],
            }
        )


class EditFamiliarWoundsScreen(ModalScreen[Wounds | None]):
    """Edits a Familiar's Wound counts and Incapacitated/Dead -- same idea
    as EditWoundsScreen, but with no Soak field: a Familiar's Soak is the
    Characteristics tab's typed-in Base Soak (Familiar.base_soak), not a
    per-Wounds figure like a Character's. Dismisses with the finished
    Wounds (its `soak` untouched), or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditFamiliarWoundsScreen {
        align: center middle;
    }

    #fam-wounds-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .famwoundsedit-row {
        width: 100%;
        height: 1;
    }

    .famwoundsedit-row Label {
        width: 22;
    }

    .famwoundsedit-row Input {
        width: 1fr;
    }

    #fam-wounds-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #fam-wounds-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, wounds: Wounds) -> None:
        super().__init__()
        self.wounds = wounds

    def compose(self) -> ComposeResult:
        w = self.wounds
        with Vertical(id="fam-wounds-dialog"):
            yield Label("Edit Wounds", id="fam-wounds-title")
            with Horizontal(classes="famwoundsedit-row"):
                yield Label("Light Wounds (-1 each)")
                yield Input(
                    value=str(w.light),
                    type="integer",
                    id="input-famwounds-light",
                    compact=True,
                )
            with Horizontal(classes="famwoundsedit-row"):
                yield Label("Medium Wounds (-3 each)")
                yield Input(
                    value=str(w.medium),
                    type="integer",
                    id="input-famwounds-medium",
                    compact=True,
                )
            with Horizontal(classes="famwoundsedit-row"):
                yield Label("Heavy Wounds (-5 each)")
                yield Input(
                    value=str(w.heavy),
                    type="integer",
                    id="input-famwounds-heavy",
                    compact=True,
                )
            yield Checkbox(
                "Incapacitated",
                value=w.incapacitated,
                id="check-famwounds-incapacitated",
                compact=True,
            )
            yield Checkbox(
                "Dead", value=w.dead, id="check-famwounds-dead", compact=True
            )
            yield Static("", id="fam-wounds-error")
            with Horizontal(id="fam-wounds-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#fam-wounds-error", Static)
        values: dict[str, object] = {"soak": self.wounds.soak}
        for label, field_name in (
            ("Light Wounds", "light"),
            ("Medium Wounds", "medium"),
            ("Heavy Wounds", "heavy"),
        ):
            raw = self.query_one(f"#input-famwounds-{field_name}", Input).value.strip()
            try:
                values[field_name] = int(raw)
            except ValueError:
                error.update(f"{label} must be a whole number.")
                return
        values["incapacitated"] = self.query_one(
            "#check-famwounds-incapacitated", Checkbox
        ).value
        values["dead"] = self.query_one("#check-famwounds-dead", Checkbox).value
        self.dismiss(Wounds(**values))


class EditCovenantScreen(ModalScreen[dict[str, object] | None]):
    """Edits the covenant-owned fields of the covenant sheet's top panel.

    The saga's name, Storyguide, current season and current year are
    inherited from the Saga and aren't editable here. Dismisses with a
    dict of field values (see _INT_FIELDS plus "name", "tribunal",
    "year_founded", "covenant_season"), or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    #: (Covenant attribute, label) for the plain whole-number fields.
    _INT_FIELDS: ClassVar[tuple[tuple[str, str], ...]] = (
        ("aegis_of_the_hearth", "Aegis of the Hearth"),
        ("aegis_penetration", "Aegis' Penetration"),
        ("living_conditions_magi", "Living Conditions (Magi)"),
        ("living_conditions_mundane", "Living Conditions (Mundane)"),
        ("aura", "Aura"),
    )

    DEFAULT_CSS = """
    EditCovenantScreen {
        align: center middle;
    }

    #cov-edit-dialog {
        width: 64;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .covedit-row {
        width: 100%;
        height: 1;
    }

    .covedit-row Label {
        width: 30;
    }

    .covedit-row Input, .covedit-row Select {
        width: 1fr;
    }

    #cov-edit-hint {
        color: $text-muted;
        height: auto;
        margin-top: 1;
    }

    #cov-edit-error {
        color: $error;
        height: auto;
    }

    #cov-edit-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, covenant: Covenant) -> None:
        super().__init__()
        self.covenant = covenant

    @staticmethod
    def _input_id(field: str) -> str:
        return f"input-cov-{field.replace('_', '-')}"

    def compose(self) -> ComposeResult:
        cov = self.covenant
        with Vertical(id="cov-edit-dialog"):
            yield Label("Edit Covenant")
            with Horizontal(classes="covedit-row"):
                yield Label("Name")
                yield Input(value=cov.name, id=self._input_id("name"), compact=True)
            with Horizontal(classes="covedit-row"):
                yield Label("Tribunal")
                yield Input(
                    value=cov.tribunal, id=self._input_id("tribunal"), compact=True
                )
            with Horizontal(classes="covedit-row"):
                yield Label("Year Founded")
                yield Input(
                    value="" if cov.year_founded is None else str(cov.year_founded),
                    type="integer",
                    id=self._input_id("year_founded"),
                    compact=True,
                )
            for field, label in self._INT_FIELDS:
                with Horizontal(classes="covedit-row"):
                    yield Label(label)
                    yield Input(
                        value=str(getattr(cov, field)),
                        type="integer",
                        id=self._input_id(field),
                        compact=True,
                    )
            with Horizontal(classes="covedit-row"):
                yield Label("Covenant Season")
                yield Select(
                    [(season, season) for season in SEASONS],
                    value=cov.covenant_season,
                    allow_blank=False,
                    id="select-cov-season",
                    compact=True,
                )
            yield Static(
                "Aura is the base aura of every laboratory in this covenant.",
                id="cov-edit-hint",
            )
            yield Static("", id="cov-edit-error")
            with Horizontal(id="cov-edit-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#cov-edit-error", Static)

        name = self.query_one(f"#{self._input_id('name')}", Input).value.strip()
        if not name:
            error.update("Name is required.")
            return

        result: dict[str, object] = {
            "name": name,
            "tribunal": self.query_one(
                f"#{self._input_id('tribunal')}", Input
            ).value.strip(),
        }

        raw_year = self.query_one(
            f"#{self._input_id('year_founded')}", Input
        ).value.strip()
        try:
            result["year_founded"] = int(raw_year) if raw_year else None
        except ValueError:
            error.update("Year Founded must be a whole number.")
            return

        for field, label in self._INT_FIELDS:
            raw = self.query_one(f"#{self._input_id(field)}", Input).value.strip()
            try:
                result[field] = int(raw)
            except ValueError:
                error.update(f"{label} must be a whole number.")
                return

        result["covenant_season"] = self.query_one("#select-cov-season", Select).value
        self.dismiss(result)


class AdvanceSeasonScreen(ModalScreen[bool]):
    """Confirms advancing the saga's calendar by one season. Dismisses with
    True to advance, False (or via Escape) to leave the date alone."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    AdvanceSeasonScreen {
        align: center middle;
    }

    #advance-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #advance-note {
        color: $text-muted;
        height: auto;
        margin-top: 1;
    }

    #advance-year-note {
        height: auto;
        margin-top: 1;
    }

    #advance-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, season: str, year: int) -> None:
        super().__init__()
        self.season = season
        self.year = year

    def compose(self) -> ComposeResult:
        new_season, new_year = next_season(self.season, self.year)
        with Vertical(id="advance-dialog"):
            yield Label("Advance Time", id="advance-title")
            yield Static(
                f"Advance the saga from {self.season} {self.year} "
                f"to {new_season} {new_year}?",
                id="advance-message",
            )
            if new_year != self.year:
                yield Static(
                    "A new year: each covenant's surplus is added to its Wealth, "
                    "and Emergency Savings start again at 0.",
                    id="advance-year-note",
                )
            yield Static(
                "Advanced by mistake? Use Set Date (T) to put the date back"
                + (" (Wealth isn't changed back)." if new_year != self.year else "."),
                id="advance-note",
            )
            with Horizontal(id="advance-buttons"):
                yield Button("Advance", id="btn-advance", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-advance")


class SetDateScreen(ModalScreen[tuple[str, int] | None]):
    """Sets the saga's calendar date directly -- for the initial date, or to
    roll back an accidental Advance. Dismisses with (season, year), or None
    if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    SetDateScreen {
        align: center middle;
    }

    #set-date-dialog {
        width: 50;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .setdate-row {
        width: 100%;
        height: 1;
    }

    .setdate-row Label {
        width: 10;
    }

    .setdate-row Input, .setdate-row Select {
        width: 1fr;
    }

    #set-date-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #set-date-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, season: str, year: int) -> None:
        super().__init__()
        self.season = season
        self.year = year

    def compose(self) -> ComposeResult:
        with Vertical(id="set-date-dialog"):
            yield Label("Set the Saga's Date", id="set-date-title")
            with Horizontal(classes="setdate-row"):
                yield Label("Season")
                yield Select(
                    [(season, season) for season in SEASONS],
                    value=self.season,
                    allow_blank=False,
                    id="select-date-season",
                    compact=True,
                )
            with Horizontal(classes="setdate-row"):
                yield Label("Year")
                yield Input(
                    value=str(self.year),
                    type="integer",
                    id="input-date-year",
                    compact=True,
                )
            yield Static("", id="set-date-error")
            with Horizontal(id="set-date-buttons"):
                yield Button("Set", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#set-date-error", Static)
        raw_year = self.query_one("#input-date-year", Input).value.strip()
        try:
            year = int(raw_year)
        except ValueError:
            error.update("Year must be a whole number.")
            return
        season = self.query_one("#select-date-season", Select).value
        self.dismiss((str(season), year))


class BoonHookDetailScreen(ModalScreen[tuple[str, str] | None]):
    """Asks for the two optional, user-written fields of a covenant
    Boon/Hook: a one-line Detail (which Edifice, which contested resource --
    shown in the list) and a multi-line Description (what the Hidden
    Resources actually contain -- shown in the details panel ahead of the
    official rules text). Both blank by default. Used when adding one and
    when editing it later. Dismisses with (detail, description), each
    stripped and possibly empty, or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    BoonHookDetailScreen {
        align: center middle;
    }

    #bh-detail-dialog {
        width: 72;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #bh-description-text {
        height: 8;
    }

    #bh-detail-hint {
        color: $text-muted;
        height: auto;
        margin: 1 0;
    }

    #bh-detail-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(
        self, kind: str, name: str, detail: str = "", description: str = ""
    ) -> None:
        super().__init__()
        self.kind = kind
        self.entry_name = name
        self.detail = detail
        self.description = description

    def compose(self) -> ComposeResult:
        with Vertical(id="bh-detail-dialog"):
            yield Label(f"{self.kind}: {self.entry_name}", id="bh-detail-title")
            yield Label("Detail (optional)")
            yield Input(
                value=self.detail,
                placeholder="e.g. the specific building or resource",
                id="input-bh-detail",
                compact=True,
            )
            yield Label("Description (optional)")
            yield TextArea(self.description, id="bh-description-text")
            yield Static(
                "Description supports **bold** and *italic*.",
                id="bh-detail-hint",
            )
            with Horizontal(id="bh-detail-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._save()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._save()

    def _save(self) -> None:
        self.dismiss(
            (
                self.query_one("#input-bh-detail", Input).value.strip(),
                self.query_one("#bh-description-text", TextArea).text.strip(),
            )
        )


class ConfirmScreen(ModalScreen[bool]):
    """A Yes/No confirmation, e.g. before deleting something. Dismisses with
    True for Yes, False for No / Escape. No is focused by default so a stray
    Enter can't delete; `y` and `n` answer directly. `message` is shown as
    markup, so escape any user text in it."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("escape", "escape", "Cancel"),
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
        border: round $accent;
        padding: 1 2;
        background: $surface;
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
        yes_variant: str = "error",
        safe_answer: bool = False,
    ) -> None:
        """`safe_answer` is the answer a stray key should give: False (No) for
        the usual "Delete X?"; True when No is the risky choice, which also
        focuses Yes and makes Escape answer Yes."""
        super().__init__()
        self.message = message
        self.yes_label = yes_label
        self.yes_variant = yes_variant
        self.safe_answer = safe_answer

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Static(self.message, id="confirm-message")
            with Horizontal(id="confirm-buttons"):
                yield Button(self.yes_label, id="btn-yes", variant=self.yes_variant)
                yield Button("No", id="btn-no")

    def on_mount(self) -> None:
        self.query_one("#btn-yes" if self.safe_answer else "#btn-no", Button).focus()

    def action_escape(self) -> None:
        self.dismiss(self.safe_answer)

    def action_yes(self) -> None:
        self.dismiss(True)

    def action_no(self) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-yes")


#: What the saga's Import Data dialog offers: (key, label, works yet?). The
#: ones that don't work yet are listed greyed out, as what's planned.
IMPORT_KINDS: tuple[tuple[str, str, bool], ...] = (
    ("characters", "Characters", False),
    ("covenants", "Covenants", False),
    ("laboratories", "Laboratories", False),
    ("books", "Books", True),
    ("spells", "Spells", True),
)


class ImportScreen(ModalScreen[str | None]):
    """Choose what to import into the saga. Kinds that can't be imported yet
    are shown greyed out and can't be chosen. Dismisses with the chosen
    IMPORT_KINDS key, or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    ImportScreen {
        align: center middle;
    }

    #import-dialog {
        width: 50;
        max-width: 100%;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #import-hint {
        color: $text-muted;
        height: auto;
        margin-bottom: 1;
    }

    #import-list {
        height: auto;
    }

    #import-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="import-dialog"):
            yield Label("Import Data", id="import-title")
            yield Static("What would you like to import?", id="import-hint")
            yield OptionList(id="import-list", compact=True)
            with Horizontal(id="import-buttons"):
                yield Button("Cancel", id="btn-import-cancel")

    def on_mount(self) -> None:
        options = self.query_one("#import-list", OptionList)
        options.add_options(
            Option(label, id=key)
            if works
            else Option(f"{label}  (not available yet)", id=key, disabled=True)
            for key, label, works in IMPORT_KINDS
        )
        options.highlighted = next(i for i, k in enumerate(IMPORT_KINDS) if k[2])
        options.focus()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        event.stop()
        self.dismiss(event.option.id)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(None)


class DuplicateBookScreen(ModalScreen[str]):
    """Asked during an import for a book whose name is already taken.
    Dismisses with "duplicate", "duplicate_all", "skip" or "skip_all" (the
    "_all" answers apply to every later duplicate of the same import). Skip
    is focused, and Escape skips, so a stray key never adds a copy."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("escape", "choose('skip')", "Skip"),
        ("d", "choose('duplicate')", "Duplicate"),
        ("D", "choose('duplicate_all')", "Duplicate All"),
        ("s", "choose('skip')", "Skip"),
        ("S", "choose('skip_all')", "Skip All"),
    ]

    DEFAULT_CSS = """
    DuplicateBookScreen {
        align: center middle;
    }

    #duplicate-dialog {
        width: 72;
        max-width: 100%;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #duplicate-message {
        height: auto;
        margin-bottom: 1;
    }

    #duplicate-buttons {
        width: 100%;
        height: auto;
    }

    #duplicate-buttons Button {
        margin-right: 1;
    }
    """

    #: (answer, button label), in button order.
    CHOICES: ClassVar[tuple[tuple[str, str], ...]] = (
        ("duplicate", "Duplicate"),
        ("duplicate_all", "Duplicate All"),
        ("skip", "Skip"),
        ("skip_all", "Skip All"),
    )

    def __init__(self, name: str, remaining: int, *, noun: str = "book") -> None:
        super().__init__()
        self.book_name = name
        self.remaining = remaining
        self.noun = noun

    def compose(self) -> ComposeResult:
        more = (
            f"\n[dim]{self.remaining} more duplicate(s) after this one.[/]"
            if self.remaining
            else ""
        )
        with Vertical(id="duplicate-dialog"):
            yield Static(
                f"A {self.noun} named [b]{escape(self.book_name)}[/] is already "
                f"in the saga. Add this one as well?{more}",
                id="duplicate-message",
            )
            with Horizontal(id="duplicate-buttons"):
                for answer, label in self.CHOICES:
                    yield Button(label, id=f"btn-{answer.replace('_', '-')}")

    def on_mount(self) -> None:
        self.query_one("#btn-skip", Button).focus()

    def action_choose(self, answer: str) -> None:
        self.dismiss(answer)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        self.dismiss((event.button.id or "btn-skip")[len("btn-") :].replace("-", "_"))


class SpellImportHelperScreen(ModalScreen[str | None]):
    """What a spell CSV looks like, with a way to save an example to start
    from. Dismisses with "choose" to go on to picking the file, or None."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    SpellImportHelperScreen {
        align: center middle;
    }

    #spell-import-dialog {
        width: 96;
        max-width: 100%;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #spell-import-body {
        height: auto;
        max-height: 30;
    }

    #spell-import-status {
        height: auto;
        margin-top: 1;
    }

    #spell-import-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }

    #spell-import-buttons Button {
        margin-right: 1;
    }
    """

    def __init__(self, folder: Path) -> None:
        super().__init__()
        self.folder = folder

    def compose(self) -> ComposeResult:
        columns = "\n".join(
            f"  [b]{name}[/]: {escape(meaning)}"
            for name, meaning in spl.CSV_COLUMN_HELP
        )
        example = escape(spl.EXAMPLE_CSV.splitlines()[1])
        with Vertical(id="spell-import-dialog"):
            yield Label("Import Spells", id="spell-import-title")
            with VerticalScroll(id="spell-import-body"):
                yield Static(
                    "Spells are imported from a CSV file with a header row into the "
                    "saga's own spells. Columns, in any order and any case:\n\n"
                    f"{columns}\n\n[b]An example row:[/]\n  [dim]{example}[/]",
                    id="spell-import-help",
                )
            yield Static("", id="spell-import-status")
            with Horizontal(id="spell-import-buttons"):
                yield Button(
                    "Choose CSV file...",
                    id="btn-spell-import-choose",
                    variant="success",
                )
                yield Button("Save example CSV", id="btn-spell-import-example")
                yield Button("Cancel", id="btn-spell-import-cancel")

    def on_mount(self) -> None:
        self._fit()
        self.query_one("#btn-spell-import-choose", Button).focus()

    def on_resize(self) -> None:
        self._fit()

    def _fit(self) -> None:
        """The help scrolls, so the buttons stay on screen however short the
        terminal is."""
        self.query_one("#spell-import-body").styles.max_height = max(
            4, min(30, self.size.height - 12)
        )

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _save_example(self) -> None:
        target = self.folder / "spells_example.csv"
        n = 2
        while target.exists():
            target = self.folder / f"spells_example_{n}.csv"
            n += 1
        status = self.query_one("#spell-import-status", Static)
        try:
            target.write_text(spl.EXAMPLE_CSV, encoding="utf-8")
        except OSError as problem:
            status.update(f"[red]Couldn't save the example: {escape(str(problem))}[/]")
            return
        status.update(
            f"Saved [b]{escape(target.name)}[/] in {escape(str(self.folder))}. "
            "Edit it, then choose it to import."
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "btn-spell-import-choose":
            self.dismiss("choose")
        elif event.button.id == "btn-spell-import-example":
            self._save_example()
        else:
            self.dismiss(None)


class _CsvDirectoryTree(DirectoryTree):
    """Folders and .csv files only (hidden entries left out)."""

    def filter_paths(self, paths):
        return [
            path
            for path in paths
            if not path.name.startswith(".")
            and (path.is_dir() or path.suffix.lower() == ".csv")
        ]


class CsvFilePickerScreen(ModalScreen[Path | None]):
    """A small file explorer for choosing a .csv file: browse the folders
    below `start` (Enter opens a folder or picks a file), Up goes to the
    parent folder, and the path box takes a typed folder or file. Dismisses
    with the chosen file, or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    CsvFilePickerScreen {
        align: center middle;
    }

    #picker-dialog {
        width: 90;
        max-width: 100%;
        height: 80%;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #picker-path-row {
        width: 100%;
        height: 1;
        margin: 1 0;
    }

    #picker-path {
        width: 1fr;
    }

    #btn-picker-up {
        margin-right: 1;
    }

    #picker-tree {
        height: 1fr;
    }

    #picker-error {
        color: $error;
        height: auto;
    }

    #picker-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, title: str, start: Path) -> None:
        super().__init__()
        self.title_text = title
        self.start = start

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-dialog"):
            yield Label(self.title_text, id="picker-title")
            with Horizontal(id="picker-path-row"):
                yield Button("Up", id="btn-picker-up", compact=True)
                yield Input(str(self.start), id="picker-path", compact=True)
            yield _CsvDirectoryTree(self.start, id="picker-tree")
            yield Static("", id="picker-error")
            with Horizontal(id="picker-buttons"):
                yield Button("Open", id="btn-picker-open", variant="success")
                yield Button("Cancel", id="btn-picker-cancel")

    def on_mount(self) -> None:
        self.query_one("#picker-tree", DirectoryTree).focus()

    def _show_folder(self, folder: Path) -> None:
        self.query_one("#picker-tree", DirectoryTree).path = folder
        self.query_one("#picker-path", Input).value = str(folder)
        self.query_one("#picker-error", Static).update("")

    def _choose(self, raw: str) -> None:
        """Open a typed folder, or pick a typed .csv file."""
        path = Path(raw.strip().strip('"')).expanduser()
        error = self.query_one("#picker-error", Static)
        if path.is_dir():
            self._show_folder(path)
        elif path.is_file() and path.suffix.lower() == ".csv":
            self.dismiss(path)
        elif path.is_file():
            error.update(f"{escape(path.name)} isn't a .csv file.")
        else:
            error.update(f"No such file or folder: {escape(str(path))}")

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        event.stop()
        self.dismiss(event.path)

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        event.stop()
        self.query_one("#picker-path", Input).value = str(event.path)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self._choose(event.value)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "btn-picker-up":
            tree = self.query_one("#picker-tree", DirectoryTree)
            self._show_folder(Path(tree.path).resolve().parent)
        elif event.button.id == "btn-picker-open":
            tree = self.query_one("#picker-tree", DirectoryTree)
            node = tree.cursor_node
            if tree.has_focus and node is not None and node.data is not None:
                self._choose(str(node.data.path))
            else:
                self._choose(self.query_one("#picker-path", Input).value)
        else:
            self.dismiss(None)


class ImproveIncomeScreen(ModalScreen[tuple[int, str] | None]):
    """Manually simulates a year's Income Modification (ArM5's automated/
    yearly advancement isn't built yet -- this is a deliberate stand-in for
    it). Choosing an Effect updates the Multiplier and Projected Income live;
    Commit confirms via ConfirmScreen, then dismisses with (new income, the
    Note to record), or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    ImproveIncomeScreen {
        align: center middle;
    }

    #improve-dialog {
        width: 70;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .improve-row {
        width: 100%;
        height: 1;
    }

    .improve-label {
        width: 26;
    }

    .improve-value {
        width: 1fr;
        color: $text-muted;
    }

    #improve-effect {
        width: 1fr;
    }

    #improve-note-label {
        margin-top: 1;
        height: 1;
    }

    #improve-note {
        color: $text-muted;
        height: auto;
    }

    #improve-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #improve-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, source: IncomeSource, current_year: int) -> None:
        super().__init__()
        self.source = source
        self.current_year = current_year

    def compose(self) -> ComposeResult:
        source = self.source
        with Vertical(id="improve-dialog"):
            yield Label(
                f"Improve {source.name or 'this source of income'}", id="improve-title"
            )
            with Horizontal(classes="improve-row"):
                yield Label("Name", classes="improve-label")
                yield Static(
                    escape(source.name or "(unnamed)"), classes="improve-value"
                )
            with Horizontal(classes="improve-row"):
                yield Label("Current Income", classes="improve-label")
                yield Static(str(source.current_income), classes="improve-value")
            with Horizontal(classes="improve-row"):
                yield Label("Annual Improvement Effect", classes="improve-label")
                yield Select(
                    [(e, e) for e in INCOME_EFFECTS],
                    value="Status Quo",
                    id="improve-effect",
                    compact=True,
                )
            with Horizontal(classes="improve-row"):
                yield Label("Income Multiplier", classes="improve-label")
                yield Static(
                    eco.income_multiplier_text("Status Quo"),
                    classes="improve-value",
                    id="improve-multiplier",
                )
            with Horizontal(classes="improve-row"):
                yield Label("Projected Income", classes="improve-label")
                yield Static(
                    str(source.current_income),
                    classes="improve-value",
                    id="improve-projected",
                )
            yield Label("Note", id="improve-note-label")
            yield Static(
                escape(source.note.strip()) if source.note.strip() else "(none)",
                id="improve-note",
            )
            yield Static("", id="improve-error")
            with Horizontal(id="improve-buttons"):
                yield Button("Commit", id="btn-commit", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-commit":
            self._try_commit()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id != "improve-effect" or not isinstance(event.value, str):
            return
        effect = event.value
        self.query_one("#improve-multiplier", Static).update(
            eco.income_multiplier_text(effect)
        )
        self.query_one("#improve-projected", Static).update(
            str(eco.projected_income(self.source.current_income, effect))
        )

    def _try_commit(self) -> None:
        effect = self.query_one("#improve-effect", Select).value
        if not isinstance(effect, str):
            self.query_one("#improve-error", Static).update("Choose an Effect.")
            return
        current = self.source.current_income
        projected = eco.projected_income(current, effect)
        note = eco.improvement_note(
            self.current_year, self.source.name, effect, current, projected
        )
        name = escape(self.source.name or "this source of income")

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                self.dismiss((projected, note))

        self.app.push_screen(
            ConfirmScreen(
                f"Update {name}'s income from {current} to {projected}?",
                yes_label="Update",
            ),
            handle_confirmed,
        )


class EditCovenantDescriptionScreen(ModalScreen[str | None]):
    """A multi-line text editor for the covenant's description. Dismisses
    with the new text, or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditCovenantDescriptionScreen {
        align: center middle;
    }

    #cov-desc-dialog {
        width: 76;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #cov-desc-text {
        height: 12;
    }

    #cov-desc-hint {
        color: $text-muted;
        height: auto;
        margin-bottom: 1;
    }

    #cov-desc-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text

    def compose(self) -> ComposeResult:
        with Vertical(id="cov-desc-dialog"):
            yield Label("Edit Covenant Description")
            yield TextArea(self.text, id="cov-desc-text")
            yield Static("Supports **bold** and *italic*.", id="cov-desc-hint")
            with Horizontal(id="cov-desc-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self.dismiss(self.query_one("#cov-desc-text", TextArea).text.rstrip())


class SelectableList(OptionList):
    """The standard "selectable list" (see DESIGN.md, UI Conventions): rows
    that each carry a selector -- a dim `○`, or a blue bold `●` on the chosen
    row -- with at most one row chosen at a time.

    Rows are `(data index, label)` pairs: the data index is the entry's
    position in whatever list the sheet keeps its data in (it becomes the
    Option id, so a filtered list still maps back to the true entry), and
    the label is markup -- escape user text with `escape()` first. An empty
    list shows one disabled "(none recorded)" row.

    A row with a `None` data index is a **header**: a disabled, unselectable
    separator (bold text, no marker) for sections whose data doesn't split
    cleanly into two side-by-side lists (e.g. Abilities' several categories,
    unlike Virtues/Flaws' two). Headers are skipped by keyboard navigation
    the same way the empty-list placeholder already is.

    Choosing a row (arrow keys or click) moves the marker and posts
    `SelectableList.Chosen(data_index)`; the owning view reacts (fills a
    details panel, clears a sibling list...). Nothing is chosen until the
    user picks a row, and `set_rows()` clears the choice.

    With `multi=True`, rows can also be *checked* for acting on several at
    once: Space (or Ctrl+click) toggles a green check in front of a row,
    independently of the chosen one, and posts `SelectableList.Checked`.
    `set_rows()` clears the checks too.
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("space", "toggle_check", "Mark"),
    ]

    DEFAULT_CSS = """
    SelectableList,
    SelectableList:focus {
        height: auto;
        max-height: 14;
        border: none;
        padding: 0;
        background: transparent;
    }

    /* The marker is the selection indicator: a solid highlight bar would
       swallow it, so the bar is neutralised (normal and focused) and the
       chosen row is just bold. */
    SelectableList > .option-list--option-highlighted,
    SelectableList:focus > .option-list--option-highlighted {
        background: transparent;
        color: $foreground;
        text-style: bold;
    }
    """

    class Chosen(Message):
        """A row was chosen; `data_index` is its entry's data index."""

        def __init__(self, selectable_list: SelectableList, data_index: int) -> None:
            super().__init__()
            self.selectable_list = selectable_list
            self.data_index = data_index

        @property
        def control(self) -> SelectableList:
            return self.selectable_list

    class Checked(Message):
        """The set of checked rows changed (multi lists only)."""

        def __init__(self, selectable_list: SelectableList) -> None:
            super().__init__()
            self.selectable_list = selectable_list

        @property
        def control(self) -> SelectableList:
            return self.selectable_list

    def __init__(
        self,
        rows: Sequence[tuple[int | None, str]] | None = None,
        *,
        id: str | None = None,
        multi: bool = False,
    ) -> None:
        super().__init__(id=id, compact=True)
        self.multi = multi
        self._rows: list[tuple[int | None, str]] = []
        self._marked: int | None = None
        self._checked: set[int] = set()  # list positions
        self._add_rows(rows or [])

    def _prompt(self, position: int) -> str:
        index, label = self._rows[position]
        if index is None:  # header row
            return f"[b]{label}[/]"
        marker = "[dodgerblue]●[/]" if position == self._marked else "[dim]○[/]"
        if not self.multi:
            return f"{marker} {label}"
        check = "[green]✔[/]" if position in self._checked else " "
        return f"{check} {marker} {label}"

    def _render_row(self, position: int | None) -> None:
        if position is not None and position < len(self._rows):
            self.replace_option_prompt_at_index(position, self._prompt(position))

    def _add_rows(self, rows: Sequence[tuple[int | None, str]]) -> None:
        # Added after construction on purpose: OptionList(*options)
        # highlights its first row, and nothing should be chosen until the
        # user picks one.
        self._rows = list(rows)
        if not self._rows:
            self.add_option(Option("[dim](none recorded)[/]", disabled=True))
            return
        self.add_options(
            Option(
                self._prompt(position),
                id=(str(index) if index is not None else None),
                disabled=index is None,
            )
            for position, (index, _) in enumerate(self._rows)
        )

    def set_rows(self, rows: Sequence[tuple[int | None, str]]) -> None:
        """Replace all rows (synchronous; nothing is chosen or checked
        afterwards)."""
        self.clear_options()
        self._marked = None
        self._checked = set()
        self._add_rows(rows)

    def relabel(self, labels: list[str]) -> None:
        """New labels for the same rows, in order (e.g. re-laid-out columns);
        the chosen row and any checks stay as they are."""
        if len(labels) != len(self._rows):
            return
        self._rows = [(index, label) for (index, _), label in zip(self._rows, labels)]
        for position in range(len(self._rows)):
            self._render_row(position)

    @property
    def selected_data_index(self) -> int | None:
        """Data index of the chosen row, or None if none is chosen."""
        option = self.highlighted_option
        return int(option.id) if option is not None and option.id else None

    @property
    def checked_data_indexes(self) -> list[int]:
        """Data indexes of the checked rows, in list order."""
        return [self._rows[p][0] for p in sorted(self._checked)]

    def clear_selection(self) -> None:
        """Unchoose everything. Posts no message."""
        self._mark(None)
        self.highlighted = None

    def _mark(self, row: int | None) -> None:
        """Move the selector marker to list position `row` (None: no marker)."""
        previous = self._marked
        if previous == row:
            return
        self._marked = row
        self._render_row(previous)
        self._render_row(row)

    def toggle_check(self, position: int) -> None:
        """Check or uncheck the row at list position `position`."""
        if not self.multi or not 0 <= position < len(self._rows):
            return
        self._checked ^= {position}
        self._render_row(position)
        self.post_message(self.Checked(self))

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "toggle_check":
            return self.multi and bool(self._rows)
        return True

    def action_toggle_check(self) -> None:
        if self.highlighted is not None:
            self.toggle_check(self.highlighted)

    async def _on_click(self, event: Click) -> None:
        if self.multi and event.ctrl:
            clicked = event.style.meta.get("option")
            if clicked is not None:
                event.stop()
                self.toggle_check(clicked)
                return
        await super()._on_click(event)

    def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        event.stop()
        if event.option.id is None:  # the disabled "(none recorded)" row
            return
        self._mark(event.option_index)
        self.post_message(self.Chosen(self, int(event.option.id)))


@dataclass
class DialogField:
    """One row of a FieldsDialog.

    `kind`: "text" (a stripped string), "int" (a whole number), "optint" (a
    whole number or blank -> None), "select" (one of `options` as (label,
    value) pairs; blank -> None when `allow_blank`), "check" (a boolean),
    "area" (multi-line text), "picker" (a button showing `display(value)`
    that opens the screen `picker(value)` returns; its result becomes the
    value) or "info" (read-only text, not returned).
    """

    key: str
    label: str
    kind: str
    value: object = None
    options: list[tuple[str, str]] = dataclass_field(default_factory=list)
    required: bool = False
    allow_blank: bool = False
    placeholder: str = ""
    hint: str = ""
    #: Shown only while this returns True for the form's current values
    #: (`FieldsDialog.current_values`); re-checked as the user edits. A hidden
    #: field is left out of the result and isn't checked.
    show_if: Callable[[dict[str, Any]], bool] | None = None
    #: A "picker" field's chooser (a screen dismissing with the new value, or
    #: None to keep the old one) and how it shows its value on the button.
    picker: Callable[[Any], Screen[Any]] | None = None
    display: Callable[[Any], str] | None = None


class FieldsDialog(ModalScreen[dict[str, Any] | None]):
    """A config-driven form: one compact row per DialogField, scrolling if the
    terminal is short (Save/Cancel stay put). Dismisses with {key: value} for
    every non-info field, or None if cancelled. `validate` gets the finished
    dict and returns an error message, or None if it's fine.

    Fields can depend on each other while the form is open: a field's
    `show_if` shows/hides it, and `live` (markup, from the current values)
    fills a line above the error, both refreshed on every change."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    FieldsDialog {
        align: center middle;
    }

    #fields-dialog {
        width: 84;
        max-width: 100%;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #fields-scroll {
        height: auto;
    }

    .fd-field {
        width: 100%;
        height: auto;
    }

    .fd-row {
        width: 100%;
        height: 1;
    }

    .fd-label {
        width: 30;
    }

    .fd-row Input, .fd-row Select, .fd-row .fd-picker {
        width: 1fr;
    }

    .fd-row .fd-picker {
        content-align: left middle;
        text-align: left;
    }

    .fd-value {
        width: 1fr;
        color: $text-muted;
    }

    .fd-area-label {
        margin-top: 1;
    }

    .fd-area {
        height: 6;
    }

    .fd-hint {
        color: $text-muted;
        height: auto;
    }

    #fields-live {
        height: auto;
        margin-top: 1;
    }

    #fields-error {
        color: $error;
        height: auto;
    }

    #fields-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        title: str,
        fields: list[DialogField],
        *,
        validate: Callable[[dict[str, Any]], str | None] | None = None,
        live: Callable[[dict[str, Any]], str] | None = None,
    ) -> None:
        super().__init__()
        self.title_text = title
        self.fields = fields
        self.validate = validate
        self.live = live
        self._picked: dict[str, Any] = {}  # "picker" fields' current values

    def compose(self) -> ComposeResult:
        with Vertical(id="fields-dialog"):
            yield Label(self.title_text, id="fields-title")
            with VerticalScroll(id="fields-scroll"):
                for spec in self.fields:
                    with Vertical(classes="fd-field", id=f"fdw-{spec.key}"):
                        yield from self._widgets(spec)
            if self.live is not None:
                yield Static("", id="fields-live")
            yield Static("", id="fields-error")
            with Horizontal(id="fields-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def _widgets(self, spec: DialogField) -> ComposeResult:
        widget_id = f"fld-{spec.key}"
        if spec.kind == "area":
            yield Label(spec.label, classes="fd-area-label")
            yield TextArea(str(spec.value or ""), id=widget_id, classes="fd-area")
            if spec.hint:
                yield Static(spec.hint, classes="fd-hint")
            return
        with Horizontal(classes="fd-row"):
            yield Label(spec.label, classes="fd-label")
            if spec.kind == "text":
                yield Input(
                    value=str(spec.value or ""),
                    placeholder=spec.placeholder,
                    id=widget_id,
                    compact=True,
                )
            elif spec.kind in ("int", "optint"):
                yield Input(
                    value="" if spec.value is None else str(spec.value),
                    type="integer",
                    id=widget_id,
                    compact=True,
                )
            elif spec.kind == "select":
                values = [value for _, value in spec.options]
                if spec.value in values:
                    current = spec.value
                elif spec.allow_blank or not values:
                    current = Select.NULL
                else:
                    current = values[0]
                yield Select(
                    spec.options,
                    value=current,
                    allow_blank=spec.allow_blank,
                    prompt=spec.placeholder or "(none)",
                    id=widget_id,
                    compact=True,
                )
            elif spec.kind == "check":
                yield Checkbox("", value=bool(spec.value), id=widget_id, compact=True)
            elif spec.kind == "picker":
                self._picked[spec.key] = spec.value
                yield Button(
                    self._picker_label(spec),
                    id=widget_id,
                    compact=True,
                    classes="fd-picker",
                )
            else:  # info
                yield Static(escape(str(spec.value)), classes="fd-value")
        if spec.hint:
            yield Static(spec.hint, classes="fd-hint")

    def on_mount(self) -> None:
        self._fit()
        self._react()

    def on_resize(self) -> None:
        self._fit()

    def _fit(self) -> None:
        """Cap the scrolling region so the title, error line and buttons always
        stay on screen, however short the terminal is."""
        reserved = 11 + (2 if self.live is not None else 0)
        self.query_one("#fields-scroll").styles.max_height = max(
            4, self.size.height - reserved
        )

    def current_values(self) -> dict[str, Any]:
        """Every non-info field's value as it stands, leniently: a number
        that doesn't parse (yet) is None; nothing is validated."""
        values: dict[str, Any] = {}
        for spec in self.fields:
            if spec.kind == "info":
                continue
            widget = self.query_one(f"#fld-{spec.key}")
            if spec.kind == "text":
                values[spec.key] = widget.value.strip()
            elif spec.kind in ("int", "optint"):
                try:
                    values[spec.key] = int(widget.value.strip())
                except ValueError:
                    values[spec.key] = None
            elif spec.kind == "select":
                values[spec.key] = (
                    widget.value if isinstance(widget.value, str) else None
                )
            elif spec.kind == "check":
                values[spec.key] = bool(widget.value)
            elif spec.kind == "picker":
                values[spec.key] = self._picked.get(spec.key)
            else:  # area
                values[spec.key] = widget.text.strip()
        return values

    def _picker_label(self, spec: DialogField) -> str:
        value = self._picked.get(spec.key)
        if value in (None, ""):
            return escape(spec.placeholder or "(choose...)")
        return escape(spec.display(value) if spec.display else str(value))

    def _open_picker(self, spec: DialogField) -> None:
        def handle_choice(choice: Any) -> None:
            if choice is None:
                return
            self._picked[spec.key] = choice
            self.query_one(f"#fld-{spec.key}", Button).label = self._picker_label(spec)
            self._react()

        self.app.push_screen(spec.picker(self._picked.get(spec.key)), handle_choice)

    def _shown(self, spec: DialogField, values: dict[str, Any]) -> bool:
        return spec.show_if is None or bool(spec.show_if(values))

    def _react(self) -> None:
        """Show/hide fields and refresh the live line for the current values."""
        if self.live is None and not any(f.show_if for f in self.fields):
            return
        values = self.current_values()
        for spec in self.fields:
            if spec.show_if is not None:
                self.query_one(f"#fdw-{spec.key}").display = self._shown(spec, values)
        if self.live is not None:
            self.query_one("#fields-live", Static).update(self.live(values))

    def on_select_changed(self, event: Select.Changed) -> None:
        self._react()

    def on_input_changed(self, event: Input.Changed) -> None:
        self._react()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        self._react()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._save()
        else:
            key = (event.button.id or "").removeprefix("fld-")
            spec = next(
                (f for f in self.fields if f.key == key and f.kind == "picker"), None
            )
            if spec is not None and spec.picker is not None:
                event.stop()
                self._open_picker(spec)

    def _save(self) -> None:
        error = self.query_one("#fields-error", Static)
        result: dict[str, Any] = {}
        current = self.current_values()
        for spec in self.fields:
            if spec.kind == "info" or not self._shown(spec, current):
                continue
            widget = self.query_one(f"#fld-{spec.key}")
            if spec.kind == "text":
                value: Any = widget.value.strip()
                if spec.required and not value:
                    error.update(f"{spec.label} is required.")
                    return
            elif spec.kind in ("int", "optint"):
                raw = widget.value.strip()
                if not raw and spec.kind == "optint":
                    value = None
                    if spec.required:
                        error.update(f"{spec.label} is required.")
                        return
                else:
                    try:
                        value = int(raw)
                    except ValueError:
                        error.update(f"{spec.label} must be a whole number.")
                        return
            elif spec.kind == "select":
                value = widget.value if isinstance(widget.value, str) else None
                if spec.required and value is None:
                    error.update(f"{spec.label} is required.")
                    return
            elif spec.kind == "check":
                value = bool(widget.value)
            elif spec.kind == "picker":
                value = self._picked.get(spec.key)
                if spec.required and value in (None, ""):
                    error.update(f"{spec.label} is required.")
                    return
            else:  # area
                value = widget.text.strip()
            result[spec.key] = value
        problem = self.validate(result) if self.validate else None
        if problem:
            error.update(problem)
            return
        self.dismiss(result)


class SheetSection(Collapsible):
    """A sheet section (on every sheet): a Collapsible that starts
    expanded. Textual's own default is collapsed, so every sheet section
    goes through this (project convention: sections are open by default,
    the user can still collapse them)."""

    def __init__(self, *children: Widget, title: str, **kwargs: Any) -> None:
        kwargs.setdefault("collapsed", False)
        super().__init__(*children, title=title, **kwargs)


def _tab_placeholder(tab_name: str) -> str:
    """Text for a not-yet-built flat placeholder tab (e.g. Diary, both on
    the covenant and character sheets)."""
    return f"{tab_name} aren't built yet -- coming in a future update."


#: The covenant Library tab's sections, where 'I' imports books into the
#: covenant's library.
_LIBRARY_SECTIONS: frozenset[str] = frozenset(
    {"section-lib-summary", "section-lib-books"}
)
#: Section ids of every book list (see BookListView); 'a' in any of them adds
#: a book, and 'e'/'A' act on books everywhere but the read-only Summary.
BOOK_SECTIONS: frozenset[str] = frozenset(
    {
        "section-lib-summary",
        "section-lib-books",
        "section-lab-books",
        "section-books",
        "section-unassigned-books",
    }
)


class BookListView(Vertical):
    """A list of books (the standard selectable list, under a column header)
    with a details panel for the chosen one.

    `books` is called whenever the list is (re)built, so it always reflects
    the saga: the covenant Library tab passes "every book in the covenant", a
    laboratory or character its own books, the saga's Unassigned Books node
    the books with no owner. Docked (Library tab, Unassigned Books), the
    list stretches down to the details panel docked below it (the Library
    tab adds a read-only Summary above it); inline (a laboratory's or
    character's Books section) the panel follows the list inside the section.
    """

    DEFAULT_CSS = """
    BookListView {
        height: auto;
    }

    BookListView.docked {
        height: 1fr;
    }

    BookListView .books-body {
        height: 1fr;
    }

    BookListView #lib-summary-body {
        width: 1fr;
        height: auto;
    }

    BookListView #lib-summary-left {
        width: 1fr;
        height: auto;
        margin-right: 4;
    }

    BookListView #lib-summary-right {
        width: 1fr;
        height: auto;
    }

    /* Docked, the book list fills the space down to the details panel. */
    BookListView.docked .books-section {
        height: 1fr;
    }

    BookListView.docked .books-section.-collapsed {
        height: auto;
    }

    BookListView.docked .books-section > Contents {
        height: 1fr;
    }

    BookListView.docked SelectableList,
    BookListView.docked SelectableList:focus {
        height: 1fr;
        max-height: 100%;
    }

    BookListView .books-header {
        width: 1fr;
        height: auto;
        color: $text-muted;
    }

    BookListView .books-panel {
        width: 1fr;
        height: auto;
        padding: 0 1;
    }

    /* With the book section's own bottom padding, two rows between the list
       and the panel. */
    BookListView.docked .books-panel {
        min-height: 6;
        max-height: 14;
        margin-top: 1;
        padding: 1 2;
        background: $panel;
    }
    """

    def __init__(
        self,
        saga: Saga,
        books: Callable[[], list[Book]],
        *,
        section_id: str,
        title: str = "Books",
        summary: bool = False,
        docked: bool = True,
    ) -> None:
        super().__init__(classes="docked" if docked else "")
        self.saga = saga
        self._books_source = books
        self.section_id = section_id
        self.title_text = title
        self.summary = summary
        self.docked = docked
        self._books: list[Book] = books()
        #: Width of the Subject column, fitted to the list (see on_resize).
        self._subject_cols = bk.SUBJECT_MIN_WIDTH

    def _title(self, checked: int = 0) -> str:
        total = sum(bk.cost(b, self.saga) for b in self._books)
        title = f"{self.title_text} ({len(self._books)}) - {total} Build Points"
        return title + (f" - {checked} marked" if checked else "")

    def _rows(self) -> list[tuple[int, str]]:
        return [
            (i, bk.row_label(self.saga, b, self._subject_cols))
            for i, b in enumerate(self._books)
        ]

    def _header(self) -> str:
        # Two more columns than the header's own indent: the check mark.
        return "  " + bk.table_header(self._subject_cols)

    def on_resize(self) -> None:
        """Give the Subject column whatever room the list has."""
        # The section's padding, then the check mark and selector (4 chars).
        cols = bk.subject_width(self.size.width - 4 - 4)
        if cols == self._subject_cols:
            return
        self._subject_cols = cols
        try:
            self.query_one(".books-header", Static).update(self._header())
            self.query_one(SelectableList).relabel([label for _, label in self._rows()])
        except NoMatches:
            return

    def _book_list(self) -> ComposeResult:
        with SheetSection(
            title=self._title(), id=self.section_id, classes="books-section"
        ):
            yield Static(self._header(), classes="books-header")
            yield SelectableList(self._rows(), id=f"{self.section_id}-list", multi=True)
            if not self.docked:
                yield Static(bk.detail_text(self.saga, None), classes="books-panel")

    def compose(self) -> ComposeResult:
        if not self.docked:
            yield from self._book_list()
            return
        with Vertical(classes="books-body"):
            if self.summary:
                left, right = bk.summary_texts(self._books, self.saga)
                with (
                    SheetSection(title="Summary", id="section-lib-summary"),
                    Horizontal(id="lib-summary-body"),
                ):
                    yield Static(left, id="lib-summary-left")
                    yield Static(right, id="lib-summary-right")
            yield from self._book_list()
        yield Static(bk.detail_text(self.saga, None), classes="books-panel")

    @property
    def books(self) -> list[Book]:
        """The books listed, in row order."""
        return self._books

    def checked_books(self) -> list[Book]:
        """The books marked (Space / Ctrl+click) for acting on together."""
        try:
            indexes = self.query_one(SelectableList).checked_data_indexes
        except NoMatches:
            return []
        return [self._books[i] for i in indexes if i < len(self._books)]

    def on_selectable_list_checked(self, event: SelectableList.Checked) -> None:
        event.stop()
        section = self.query_one(f"#{self.section_id}", Collapsible)
        section.title = self._title(len(self.checked_books()))

    def selected_book(self) -> Book | None:
        index = self.query_one(SelectableList).selected_data_index
        return (
            self._books[index]
            if index is not None and index < len(self._books)
            else None
        )

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        event.stop()
        book = (
            self._books[event.data_index]
            if event.data_index < len(self._books)
            else None
        )
        self.query_one(".books-panel", Static).update(bk.detail_text(self.saga, book))

    def rebuild(self) -> None:
        """Re-read the books (an edit can add one, remove one or move it to
        another owner's list) and re-render; the chosen book stays chosen if
        it's still listed, with its panel refreshed."""
        try:
            chosen = self.selected_book()
            self._books = self._books_source()
            self.query_one(f"#{self.section_id}", Collapsible).title = self._title()
            if self.summary:
                left, right = bk.summary_texts(self._books, self.saga)
                self.query_one("#lib-summary-left", Static).update(left)
                self.query_one("#lib-summary-right", Static).update(right)
            rows = self.query_one(SelectableList)
            rows.set_rows(self._rows())
            panel = self.query_one(".books-panel", Static)
            if chosen is not None and any(b is chosen for b in self._books):
                # Posts Chosen, which refreshes the panel.
                rows.highlighted = next(
                    i for i, b in enumerate(self._books) if b is chosen
                )
            else:
                panel.update(bk.detail_text(self.saga, None))
        except NoMatches:
            return  # the sheet is being replaced


#: The Spells view's list section (a/A/e act on the saga's own spells).
SPELL_SECTION = "section-spells"


class SpellListView(Vertical):
    """The saga's Spells view: a filter bar, the list of spells (the catalog
    plus the saga's own) stretching down to a scrolling details panel.

    Filters apply as they change: a search over name and description (every
    word must match), Technique, Form (both also match a requisite), Ritual,
    Source (a book, or the saga's own), and a level range (General spells pass
    any range). The section title shows how many of how many are listed.
    """

    DEFAULT_CSS = """
    SpellListView {
        height: 1fr;
    }

    SpellListView #spell-filters {
        height: auto;
        padding: 0 1;
    }

    SpellListView .spell-filter-row {
        height: 1;
        width: 1fr;
        margin-bottom: 1;
    }

    SpellListView #spell-search {
        width: 1fr;
        margin-right: 2;
    }

    SpellListView .spell-filter-row Select {
        width: 20;
        margin-right: 1;
    }

    SpellListView .spell-filter-label {
        width: auto;
        margin-right: 1;
        color: $text-muted;
    }

    SpellListView .spell-level {
        width: 7;
        margin-right: 1;
    }

    /* The list and the panel share the height 2:1, so both stay usable on
       a small terminal. */
    SpellListView #section-spells {
        height: 2fr;
    }

    SpellListView #section-spells.-collapsed {
        height: auto;
    }

    SpellListView #section-spells > Contents {
        height: 1fr;
    }

    SpellListView .spells-header {
        width: 1fr;
        height: auto;
        color: $text-muted;
    }

    SpellListView SelectableList,
    SpellListView SelectableList:focus {
        height: 1fr;
        max-height: 100%;
    }

    SpellListView #spell-panel {
        height: 1fr;
        min-height: 4;
        margin-top: 1;
        padding: 1 2;
        background: $panel;
    }
    """

    def __init__(self, saga: Saga) -> None:
        super().__init__()
        self.saga = saga
        self._all: list[Spell] = spl.all_spells(saga)
        self._shown: list[Spell] = list(self._all)

    def compose(self) -> ComposeResult:
        arts_blank = "(any)"
        with Vertical(id="spell-filters"):
            with Horizontal(classes="spell-filter-row"):
                yield Input(
                    placeholder="Search spell names and descriptions...",
                    id="spell-search",
                    compact=True,
                )
                yield Select(
                    [(f"{key} - {name}", key) for key, name in SPELL_SOURCES.items()]
                    + [("The saga's own", spl.OWN_SOURCE)],
                    prompt="Source: any",
                    id="spell-source",
                    compact=True,
                )
            with Horizontal(classes="spell-filter-row"):
                yield Select(
                    [(t, t) for t in TECHNIQUES],
                    prompt=f"Technique: {arts_blank}",
                    id="spell-technique",
                    compact=True,
                )
                yield Select(
                    [(f, f) for f in FORMS],
                    prompt=f"Form: {arts_blank}",
                    id="spell-form",
                    compact=True,
                )
                yield Select(
                    [("Rituals", "yes"), ("Formulaic", "no")],
                    prompt="Ritual: any",
                    id="spell-ritual",
                    compact=True,
                )
                yield Label("Level", classes="spell-filter-label")
                yield Input(
                    placeholder="from",
                    type="integer",
                    id="spell-min-level",
                    classes="spell-level",
                    compact=True,
                )
                yield Input(
                    placeholder="to",
                    type="integer",
                    id="spell-max-level",
                    classes="spell-level",
                    compact=True,
                )
        with SheetSection(title=self._title(), id=SPELL_SECTION):
            yield Static(spl.table_header(), classes="spells-header")
            yield SelectableList(self._rows(), id="spell-list")
        with VerticalScroll(id="spell-panel"):
            yield Static(spl.detail_text(self.saga, None), id="spell-panel-text")

    def _title(self) -> str:
        return f"Spells ({len(self._shown)} of {len(self._all)})"

    def _rows(self) -> list[tuple[int, str]]:
        return [(i, spl.row_label(self.saga, s)) for i, s in enumerate(self._shown)]

    @property
    def shown(self) -> list[Spell]:
        """The spells listed, in row order (after the filters)."""
        return self._shown

    def selected_spell(self) -> Spell | None:
        index = self.query_one("#spell-list", SelectableList).selected_data_index
        return (
            self._shown[index]
            if index is not None and index < len(self._shown)
            else None
        )

    def _filters(self) -> dict[str, Any]:
        def select(widget_id: str) -> str | None:
            value = self.query_one(widget_id, Select).value
            return value if isinstance(value, str) else None

        def number(widget_id: str) -> int | None:
            try:
                return int(self.query_one(widget_id, Input).value)
            except ValueError:
                return None

        ritual = select("#spell-ritual")
        return {
            "text": self.query_one("#spell-search", Input).value,
            "technique": select("#spell-technique"),
            "form": select("#spell-form"),
            "ritual": None if ritual is None else ritual == "yes",
            "source": select("#spell-source"),
            "min_level": number("#spell-min-level"),
            "max_level": number("#spell-max-level"),
        }

    def refilter(self) -> None:
        """Re-apply the filters (and re-read the spells, after an edit); the
        chosen spell stays chosen if it's still listed."""
        try:
            chosen = self.selected_spell()
            self._all = spl.all_spells(self.saga)
            self._shown = spl.filter_spells(self.saga, self._all, **self._filters())
            self.query_one(f"#{SPELL_SECTION}", Collapsible).title = self._title()
            rows = self.query_one("#spell-list", SelectableList)
            rows.set_rows(self._rows())
            position = next(
                (i for i, sp in enumerate(self._shown) if sp is chosen), None
            )
            if position is not None:
                rows.highlighted = position  # posts Chosen -> refreshes the panel
            else:
                self._show(None)
        except NoMatches:
            return

    def _show(self, spell: Spell | None) -> None:
        self.query_one("#spell-panel-text", Static).update(
            spl.detail_text(self.saga, spell)
        )
        self.query_one("#spell-panel", VerticalScroll).scroll_home(animate=False)

    def on_input_changed(self, event: Input.Changed) -> None:
        event.stop()
        self.refilter()

    def on_select_changed(self, event: Select.Changed) -> None:
        event.stop()
        self.refilter()

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        event.stop()
        index = event.data_index
        self._show(self._shown[index] if index < len(self._shown) else None)


class CharacterSheetView(Vertical):
    """The character sheet mounted into WorkspaceScreen's detail pane.

    A fixed top panel (Info above Characteristics -- not inside any tab,
    permanently expanded, same PinnedCollapsible pattern as
    CovenantSheetView/LaboratorySheetView) above the tabbed body. This is
    STORY-207's finished layout -- tab order: Description, Abilities,
    Virtues & Flaws, Hermetic Magic (magi only), Inventory, Laboratory
    (magi only), Diary.

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
      (a PinnedCollapsible, not a toggleable SheetSection -- two side-by-
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
    - Laboratory (tab, id "tab-lab", magi only) and Diary (tab, id
      "tab-diary", every character type): flat placeholder panes, no
      Collapsible, mirroring CovenantSheetView's own Diary placeholder
      (see the module-level _tab_placeholder() helper both share). Neither
      is in _CHARACTER_DISPATCH_TABS, so switching to either clears focus
      and 'e' falls back to editing the top panel -- the flat-tab
      focus-fallback logic every earlier slice set up for exactly this.
    """

    DEFAULT_CSS = """
    CharacterSheetView {
        height: 1fr;
    }

    CharacterSheetView #char-top-panel {
        width: 1fr;
        height: auto;
    }

    CharacterSheetView #char-info-body {
        width: 1fr;
        height: auto;
    }

    CharacterSheetView #char-info-left,
    CharacterSheetView #char-info-right {
        width: 1fr;
        height: auto;
    }

    CharacterSheetView #char-biographical-row,
    CharacterSheetView #hermetic-background-row,
    CharacterSheetView #char-health-row,
    CharacterSheetView #pt-rep-row {
        width: 1fr;
        height: auto;
    }

    CharacterSheetView #char-biographical-left,
    CharacterSheetView #char-biographical-right,
    CharacterSheetView #hermetic-background-left,
    CharacterSheetView #hermetic-background-right,
    CharacterSheetView #char-health-wounds-col,
    CharacterSheetView #char-health-fatigue-col {
        width: 1fr;
        height: auto;
    }

    CharacterSheetView #pt-rep-row SheetSection {
        width: 1fr;
    }

    CharacterSheetView #vf-row {
        width: 1fr;
        height: auto;
    }

    CharacterSheetView #section-vf-virtues {
        margin-right: 2;
    }

    CharacterSheetView TabbedContent {
        height: 1fr;
    }

    CharacterSheetView TabPane {
        padding: 1 0;
    }

    CharacterSheetView VerticalScroll {
        height: 1fr;
        width: 1fr;
    }

    /* Every selectable-list details panel: a gap below the list, its own
       shaded background so it reads as a distinct panel (matching the saga
       Spells view and every covenant list). */
    CharacterSheetView #ability-info,
    CharacterSheetView #vf-info,
    CharacterSheetView #inventory-info,
    CharacterSheetView #hermetic-info {
        width: 1fr;
        height: auto;
        min-height: 6;
        margin-top: 1;
        padding: 1 2;
        background: $panel;
    }

    CharacterSheetView #hermetic-body {
        height: 1fr;
    }

    CharacterSheetView #arts-row {
        width: 1fr;
        height: auto;
    }

    CharacterSheetView #arts-techniques-col,
    CharacterSheetView #arts-forms-col {
        width: 1fr;
        height: auto;
    }

    CharacterSheetView #arts-techniques-col {
        margin-right: 2;
    }

    CharacterSheetView .arts-col-title {
        text-style: bold;
    }

    CharacterSheetView .arts-header {
        color: $text-muted;
    }
    """

    def __init__(self, saga: Saga, character: Character) -> None:
        super().__init__()
        self.saga = saga
        self.character = character
        #: Set once TabbedContent's initial TabActivated has been seen -- see
        #: WorkspaceScreen.on_tabbed_content_tab_activated().
        self.initial_tab_seen = False

    def compose(self) -> ComposeResult:
        character = self.character
        with Vertical(id="char-top-panel"):
            with PinnedCollapsible(
                title=escape(character.name), id="section-char-info"
            ):
                with Horizontal(id="char-info-body"):
                    yield Static(self._info_left_text(), id="char-info-left")
                    yield Static(self._info_right_text(), id="char-info-right")
                yield Button("Edit (e)", id="btn-char-info-edit", compact=True)
            with PinnedCollapsible(
                title="Characteristics", id="section-char-characteristics"
            ):
                yield Static(
                    self._characteristics_text(), id="char-characteristics-content"
                )
                yield Button(
                    "Edit (e)", id="btn-char-characteristics-edit", compact=True
                )
        with TabbedContent(initial="tab-description"):
            with TabPane("Description", id="tab-description"), VerticalScroll():
                if character.type == "magus":
                    with (
                        SheetSection(
                            title="Hermetic Background",
                            id="section-hermetic-background",
                        ),
                        Horizontal(id="hermetic-background-row"),
                    ):
                        yield Static(
                            self._hermetic_background_left_text(),
                            id="hermetic-background-left",
                        )
                        yield Static(
                            self._hermetic_background_right_text(),
                            id="hermetic-background-right",
                        )
                with (
                    SheetSection(
                        title="Biographical Detail", id="section-char-biographical"
                    ),
                    Horizontal(id="char-biographical-row"),
                ):
                    yield Static(
                        self._biographical_left_text(), id="char-biographical-left"
                    )
                    yield Static(
                        self._biographical_right_text(),
                        id="char-biographical-right",
                    )
                with Horizontal(id="pt-rep-row"):
                    with SheetSection(
                        title="Personality Traits", id="section-personality-traits"
                    ):
                        yield SelectableList(
                            self._personality_trait_rows(),
                            id="personality-traits-list",
                        )
                    with SheetSection(title="Reputations", id="section-reputations"):
                        yield SelectableList(
                            self._reputation_rows(), id="character-reputations-list"
                        )
                with SheetSection(title="Aging & Warping", id="section-aging"):
                    yield Static(self._aging_text(), id="aging-content")
                with (
                    SheetSection(title="Health", id="section-char-health"),
                    Horizontal(id="char-health-row"),
                ):
                    with Vertical(id="char-health-wounds-col"):
                        yield Static(self._wounds_text(), id="wounds-content")
                        yield Button(
                            "Edit Wounds (e)",
                            id="btn-char-health-wounds-edit",
                            compact=True,
                        )
                    with Vertical(id="char-health-fatigue-col"):
                        yield Static(self._fatigue_text(), id="fatigue-content")
                        yield Button(
                            "Edit Fatigue",
                            id="btn-char-health-fatigue-edit",
                            compact=True,
                        )
            with TabPane("Abilities", id="tab-abilities"), VerticalScroll():
                yield SelectableList(self._ability_rows(), id="abilities-list")
                yield Static(self._ability_info_text(None), id="ability-info")
            with TabPane("Virtues & Flaws", id="tab-vf"), VerticalScroll():
                with Horizontal(id="vf-row"):
                    with SheetSection(title="Virtues", id="section-vf-virtues"):
                        yield SelectableList(
                            self._vf_rows("Virtue"), id="vf-virtues-list"
                        )
                    with SheetSection(title="Flaws", id="section-vf-flaws"):
                        yield SelectableList(self._vf_rows("Flaw"), id="vf-flaws-list")
                yield Static(self._vf_info_text(None), id="vf-info")
            if character.type == "magus":
                with (
                    TabPane("Hermetic Magic", id="tab-hermetic"),
                    Vertical(id="hermetic-body"),
                ):
                    with VerticalScroll(id="hermetic-scroll"):
                        with (
                            PinnedCollapsible(title="Magical Arts", id="section-arts"),
                            Horizontal(id="arts-row"),
                        ):
                            with Vertical(id="arts-techniques-col"):
                                yield Static("Techniques", classes="arts-col-title")
                                yield Static(
                                    self._arts_header_text(),
                                    classes="arts-header",
                                )
                                yield SelectableList(
                                    self._arts_rows(TECHNIQUES),
                                    id="arts-techniques-list",
                                )
                            with Vertical(id="arts-forms-col"):
                                yield Static("Forms", classes="arts-col-title")
                                yield Static(
                                    self._arts_header_text(),
                                    classes="arts-header",
                                )
                                yield SelectableList(
                                    self._arts_rows(FORMS),
                                    id="arts-forms-list",
                                )
                        with SheetSection(
                            title="Raw Vis", id="section-raw-vis-hermetic"
                        ):
                            yield SelectableList(
                                self._raw_vis_rows(), id="raw-vis-list-hermetic"
                            )
                        with SheetSection(
                            title="Known Spells", id="section-known-spells"
                        ):
                            yield SelectableList(
                                self._known_spell_rows(), id="known-spells-list"
                            )
                    yield Static(
                        "[dim]Select an Art or a Known Spell to see its details.[/]",
                        id="hermetic-info",
                    )
            with (
                TabPane("Inventory", id="tab-inventory"),
                VerticalScroll(),
            ):
                if character.type == "magus":
                    with SheetSection(title="Raw Vis", id="section-raw-vis-inventory"):
                        yield SelectableList(
                            self._raw_vis_rows(), id="raw-vis-list-inventory"
                        )
                with SheetSection(title="Personal Gear", id="section-inventory"):
                    yield SelectableList(self._inventory_rows(), id="inventory-list")
                    yield Static(self._inventory_info_text(None), id="inventory-info")
                yield BookListView(
                    self.saga,
                    lambda: bk.books_owned_by(self.saga, "character", character.id),
                    section_id="section-books",
                    docked=False,
                )
            if character.type == "magus":
                with TabPane("Laboratory", id="tab-lab"):
                    yield Static(_tab_placeholder("Laboratory"))
            with TabPane("Diary", id="tab-diary"):
                yield Static(_tab_placeholder("Diary"))

    #: Bare Collapsible-section ids, except "tab-abilities" which has no
    #: sub-sections (a single flat pane, keyed by its own tab id) -- see
    #: WorkspaceScreen._active_section(). Sections with more than
    #: one Static (Biographical Detail, Hermetic Background, Health) are
    #: special-cased in refresh_section() instead of listed here.
    _SECTION_CONTENT: ClassVar[dict[str, str]] = {
        "section-aging": "#aging-content",
    }
    _SECTION_TEXT: ClassVar[dict[str, str]] = {
        "section-aging": "_aging_text",
    }

    def refresh_section(self, section_id: str) -> None:
        if section_id == "section-char-info":
            try:
                self.query_one("#char-info-left", Static).update(self._info_left_text())
                self.query_one("#char-info-right", Static).update(
                    self._info_right_text()
                )
                self.query_one(
                    "#section-char-info", Collapsible
                ).title = self.character.name
            except NoMatches:
                pass
            return
        if section_id == "section-char-characteristics":
            try:
                self.query_one("#char-characteristics-content", Static).update(
                    self._characteristics_text()
                )
            except NoMatches:
                pass
            return
        if section_id == "tab-abilities":
            try:
                self.query_one("#abilities-list", SelectableList).set_rows(
                    self._ability_rows()
                )
                self.query_one("#ability-info", Static).update(
                    self._ability_info_text(None)
                )
            except NoMatches:
                pass
            return
        if section_id == "section-known-spells":
            try:
                self.query_one("#known-spells-list", SelectableList).set_rows(
                    self._known_spell_rows()
                )
            except NoMatches:
                pass
            self._refresh_hermetic_info()
            return
        if section_id == "section-arts":
            try:
                self.query_one("#arts-techniques-list", SelectableList).set_rows(
                    self._arts_rows(TECHNIQUES)
                )
                self.query_one("#arts-forms-list", SelectableList).set_rows(
                    self._arts_rows(FORMS)
                )
            except NoMatches:
                pass
            self._refresh_hermetic_info()
            return
        if section_id == "section-inventory":
            try:
                self.query_one("#inventory-list", SelectableList).set_rows(
                    self._inventory_rows()
                )
                self.query_one("#inventory-info", Static).update(
                    self._inventory_info_text(None)
                )
            except NoMatches:
                pass
            return
        if section_id == "section-personality-traits":
            try:
                self.query_one("#personality-traits-list", SelectableList).set_rows(
                    self._personality_trait_rows()
                )
            except NoMatches:
                pass
            return
        if section_id == "section-reputations":
            try:
                self.query_one("#character-reputations-list", SelectableList).set_rows(
                    self._reputation_rows()
                )
            except NoMatches:
                pass
            return
        if section_id in ("section-raw-vis-hermetic", "section-raw-vis-inventory"):
            # Raw Vis deliberately appears twice (Hermetic Magic and
            # Inventory tabs), both backed by character.raw_vis and both
            # mounted at once (TabbedContent keeps inactive panes mounted,
            # just hidden) -- refresh both lists regardless of which of the
            # two section ids triggered this, so neither goes stale.
            try:
                self.query_one("#raw-vis-list-hermetic", SelectableList).set_rows(
                    self._raw_vis_rows()
                )
            except NoMatches:
                pass
            try:
                self.query_one("#raw-vis-list-inventory", SelectableList).set_rows(
                    self._raw_vis_rows()
                )
            except NoMatches:
                pass
            return
        if section_id in ("section-vf-virtues", "section-vf-flaws"):
            try:
                self.query_one("#vf-virtues-list", SelectableList).set_rows(
                    self._vf_rows("Virtue")
                )
                self.query_one("#vf-flaws-list", SelectableList).set_rows(
                    self._vf_rows("Flaw")
                )
                self.query_one("#vf-info", Static).update(self._vf_info_text(None))
            except NoMatches:
                pass
            return
        if section_id == "section-char-biographical":
            try:
                self.query_one("#char-biographical-left", Static).update(
                    self._biographical_left_text()
                )
                self.query_one("#char-biographical-right", Static).update(
                    self._biographical_right_text()
                )
            except NoMatches:
                pass
            return
        if section_id == "section-hermetic-background":
            try:
                self.query_one("#hermetic-background-left", Static).update(
                    self._hermetic_background_left_text()
                )
                self.query_one("#hermetic-background-right", Static).update(
                    self._hermetic_background_right_text()
                )
            except NoMatches:
                pass
            return
        if section_id == "section-char-health":
            try:
                self.query_one("#wounds-content", Static).update(self._wounds_text())
                self.query_one("#fatigue-content", Static).update(self._fatigue_text())
            except NoMatches:
                pass
            return
        selector = self._SECTION_CONTENT.get(section_id)
        text_method = self._SECTION_TEXT.get(section_id)
        if selector is None or text_method is None:
            return
        try:
            static = self.query_one(selector, Static)
        except NoMatches:
            return
        static.update(getattr(self, text_method)())

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
        if list_id == "abilities-list":
            event.stop()
            self.query_one("#ability-info", Static).update(
                self._ability_info_text(event.data_index)
            )
            return
        if list_id == "inventory-list":
            event.stop()
            self.query_one("#inventory-info", Static).update(
                self._inventory_info_text(event.data_index)
            )
            return
        if list_id in ("arts-techniques-list", "arts-forms-list", "known-spells-list"):
            event.stop()
            # Only one of the three Hermetic Magic lists has a selection at
            # a time -- they share one details panel.
            for other_id in (
                "arts-techniques-list",
                "arts-forms-list",
                "known-spells-list",
            ):
                if other_id != list_id:
                    self.query_one(f"#{other_id}", SelectableList).clear_selection()
            self._refresh_hermetic_info()
            return
        if list_id not in ("vf-virtues-list", "vf-flaws-list"):
            return
        event.stop()
        # A Virtue or Flaw row was chosen: unchoose the sibling list (one
        # selection across both) and fill the details panel.
        other = "vf-flaws-list" if list_id == "vf-virtues-list" else "vf-virtues-list"
        self.query_one(f"#{other}", SelectableList).clear_selection()
        self.query_one("#vf-info", Static).update(self._vf_info_text(event.data_index))

    @staticmethod
    def _inherited(value: str) -> str:
        """Dim a value that's derived/inherited and isn't edited here."""
        return f"[dim]{escape(value)}[/]"

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
            ("Size", str(b.size)),
        ]
        return aligned(rows)

    def _biographical_left_text(self) -> str:
        """Column 1 of Biographical Detail: every field except Biography
        (column 2, see _biographical_right_text()) -- the remaining
        Background fields (Setting/Confidence/Size live in the top panel)
        plus every Description field but the free-text Biography box."""
        b, d = self.character.background, self.character.description
        return "\n".join(
            [
                f"Player: {escape(b.player) or '(not set)'}",
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
        docstring in models.py)."""
        return escape(self.character.description.biography) or "(none recorded)"

    def _characteristics_text(self) -> str:
        return st.characteristics_text(self.character.characteristics)

    def _ability_rows(self) -> list[tuple[int | None, str]]:
        return st.ability_rows(self.character.abilities)

    def _ability_info_text(self, index: int | None) -> str:
        return st.ability_info_text(self.character.abilities, index)

    def _vf_rows(self, vf_type: str) -> list[tuple[int | None, str]]:
        return st.vf_rows(self.character.virtues_flaws, vf_type)

    def _vf_info_text(self, index: int | None) -> str:
        return st.vf_info_text(self.character.virtues_flaws, index)

    def _aging_text(self) -> str:
        a = self.character.aging
        return "\n".join(
            [
                f"Decrepitude: {a.decrepitude}",
                "Effects of Aging:",
                escape(a.effects) or "(none recorded)",
                "",
                f"Warping: {a.warping_score}/{a.warping_points}",
            ]
        )

    def _personality_trait_rows(self) -> list[tuple[int | None, str]]:
        return st.trait_rows(self.character.personality_traits)

    def _reputation_rows(self) -> list[tuple[int | None, str]]:
        # Unsigned, unlike every other Reputation list (STORY-1109 B14).
        return st.trait_rows(self.character.reputations, signed=False)

    def _wounds_text(self) -> str:
        return st.wounds_text(self.character.wounds, with_soak=True)

    def _fatigue_text(self) -> str:
        return st.fatigue_text(self.character.fatigue_level)

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
        """Column 2 of Hermetic Background: just Wizard's Sigil."""
        sigil = self.character.hermetic.wizards_sigil
        return f"Wizard's Sigil: {escape(sigil) or '(not set)'}"

    _ARTS_NAME_WIDTH: ClassVar[int] = 16
    _ARTS_NUM_WIDTH: ClassVar[int] = 6

    def _arts_header_text(self) -> str:
        """Column titles above an Arts list, aligned with _art_row_label()
        (the two-character indent is the list's selector marker)."""
        return (
            f"  {'':<{self._ARTS_NAME_WIDTH}}"
            f"{'Level':>{self._ARTS_NUM_WIDTH}}{'XP':>{self._ARTS_NUM_WIDTH}}"
        )

    def _art_row_label(self, art: str) -> str:
        score = self.character.arts.get(art.lower(), ArtScore())
        name = f"{art} ({ART_ABBREVIATIONS[art]})"
        return (
            f"{name:<{self._ARTS_NAME_WIDTH}}"
            f"{score.level:>{self._ARTS_NUM_WIDTH}}{score.xp:>{self._ARTS_NUM_WIDTH}}"
        )

    def _arts_rows(self, arts: Sequence[str]) -> list[tuple[int, str]]:
        return [(i, self._art_row_label(art)) for i, art in enumerate(arts)]

    def _art_info_text(self, art: str) -> str:
        score = self.character.arts.get(art.lower(), ArtScore())
        return "\n".join(
            [
                f"[b]Name:[/] {art} ({ART_ABBREVIATIONS[art]})",
                f"[b]Level:[/] {score.level}    [b]XP:[/] {score.xp}",
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
        index = self.query_one("#known-spells-list", SelectableList).selected_data_index
        info.update(self._known_spell_info_text(index))

    def _known_spell_rows(self) -> list[tuple[int | None, str]]:
        rows: list[tuple[int | None, str]] = []
        for index, known in enumerate(self.character.spells_known):
            spell = spl.find_spell(self.saga, known.spell_id)
            if spell is None:
                rows.append((index, f"{escape(known.spell_id)} (unknown spell)"))
                continue
            label = spl.row_label(self.saga, spell)
            if known.mastery_score:
                label += f"  [b]Mastery {known.mastery_score}[/]"
            rows.append((index, label))
        return rows

    def _known_spell_info_text(self, index: int | None) -> str:
        if index is None:
            return "[dim]Select a spell to see its details.[/]"
        known = self.character.spells_known[index]
        spell = spl.find_spell(self.saga, known.spell_id)
        if spell is None:
            lines = [f"[red]Unknown spell: {escape(known.spell_id)}[/]"]
        else:
            lines = [spl.detail_text(self.saga, spell)]
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
        """One selectable list for all of Inventory, with a header row before
        each non-empty kind (Weapons, Armor, Other Items)."""
        rows: list[tuple[int | None, str]] = []
        for kind in self._INVENTORY_KINDS:
            indexed = [
                (i, item)
                for i, item in enumerate(self.character.inventory)
                if item.kind == kind
            ]
            if not indexed:
                continue
            rows.append((None, self._INVENTORY_HEADERS[kind]))
            for index, item in indexed:
                rows.append((index, pos.row_label(pos.PossessionEntry(kind, item))))
        return rows

    def _inventory_info_text(self, index: int | None) -> str:
        if index is None:
            return "[dim]Select an item for its details.[/]"
        item = self.character.inventory[index]
        return pos.detail_text(pos.PossessionEntry(item.kind, item))


class PinnedCollapsible(Collapsible):
    """A Collapsible that is permanently expanded and ignores toggling.

    Used for each sheet's always-visible top panel (and the Arts panel). It
    stays a real Collapsible (with a focusable CollapsibleTitle) so the
    focus-ancestry dispatch in WorkspaceScreen treats it like every other
    section, but it can never be collapsed.
    """

    def __init__(self, *children: Widget, title: str, id: str | None = None) -> None:
        super().__init__(
            *children, title=title, collapsed=False, expanded_symbol="", id=id
        )

    def _on_collapsible_title_toggle(self, event: Message) -> None:
        # Textual dispatches a message to every class in the MRO's handler
        # of the same name, so stop() alone isn't enough -- prevent_default()
        # is what keeps Collapsible's own handler from flipping `collapsed`.
        event.stop()
        event.prevent_default()

    def on_click(self, event: Click) -> None:
        # Clicking anywhere in the section (not just its title) makes it the
        # active section, so 'e' and the Footer hint work after a click.
        self.query_one("CollapsibleTitle").focus()


class LaboratorySheetView(Vertical):
    """The laboratory sheet mounted into WorkspaceScreen's detail pane.

    A fixed top panel (Identity above Characteristics -- not inside any
    tab, permanently expanded) above a 5-tab body mirroring the
    sheet's own pages: Planning (placeholder), Virtues & Flaws, Attributes
    (Specialties/Features/Rooms), Inventory (Raw Vis/Items), Diary. Its
    lists are still read-only Statics edited through pickers, not the
    selectable lists the other sheets use (STORY-303).
    """

    DEFAULT_CSS = """
    LaboratorySheetView {
        height: 1fr;
    }

    LaboratorySheetView #lab-top-panel {
        width: 1fr;
        height: auto;
    }

    LaboratorySheetView #lab-characteristics-body {
        width: 1fr;
        height: auto;
    }

    LaboratorySheetView #lab-characteristics-derived {
        width: auto;
        height: auto;
        margin-right: 6;
    }

    LaboratorySheetView #lab-characteristics-content {
        width: auto;
        height: auto;
    }

    LaboratorySheetView TabbedContent {
        height: 1fr;
    }

    LaboratorySheetView TabPane {
        padding: 1 0;
    }

    LaboratorySheetView VerticalScroll {
        height: 1fr;
        width: 1fr;
    }
    """

    def __init__(self, saga: Saga, laboratory: Laboratory) -> None:
        super().__init__()
        self.saga = saga
        self.laboratory = laboratory
        #: Set once TabbedContent's initial TabActivated has been seen -- see
        #: WorkspaceScreen.on_tabbed_content_tab_activated().
        self.initial_tab_seen = False

    def compose(self) -> ComposeResult:
        with Vertical(id="lab-top-panel"):
            with PinnedCollapsible(title="Identity", id="section-lab-identity"):
                yield Static(self._identity_text(), id="lab-identity-content")
                yield Button("Edit (e)", id="btn-lab-identity-edit", compact=True)
            with PinnedCollapsible(
                title="Characteristics", id="section-lab-characteristics"
            ):
                with Horizontal(id="lab-characteristics-body"):
                    yield Static(
                        self._characteristics_derived_text(),
                        id="lab-characteristics-derived",
                    )
                    yield Static(
                        self._characteristics_table_text(),
                        id="lab-characteristics-content",
                    )
                yield Button(
                    "Edit (e)", id="btn-lab-characteristics-edit", compact=True
                )
        with TabbedContent(initial="tab-lab-planning"):
            with TabPane("Planning", id="tab-lab-planning"):
                yield Static(self._planning_text(), id="lab-planning-content")
            with TabPane("Virtues & Flaws", id="tab-lab-vf"):
                yield Static(self._vf_text(), id="lab-vf-content")
            with TabPane("Attributes", id="tab-lab-attributes"), VerticalScroll():
                with SheetSection(title="Specialties", id="section-lab-specialties"):
                    yield Static(self._specialties_text(), id="lab-specialties-content")
                with SheetSection(title="Features", id="section-lab-features"):
                    yield Static(self._features_text(), id="lab-features-content")
                with SheetSection(title="Rooms", id="section-lab-rooms"):
                    yield Static(self._rooms_text(), id="lab-rooms-content")
            with TabPane("Inventory", id="tab-lab-inventory"), VerticalScroll():
                with SheetSection(title="Raw Vis", id="section-lab-raw-vis"):
                    yield Static(self._raw_vis_text(), id="lab-raw-vis-content")
                with SheetSection(title="Items", id="section-lab-items"):
                    yield Static(self._items_text(), id="lab-items-content")
                yield BookListView(
                    self.saga,
                    lambda: bk.books_owned_by(
                        self.saga, "laboratory", self.laboratory.id
                    ),
                    section_id="section-lab-books",
                    docked=False,
                )
            with TabPane("Diary", id="tab-lab-diary"):
                yield Static(self._diary_text(), id="lab-diary-content")

    _SECTION_CONTENT: ClassVar[dict[str, str]] = {
        "section-lab-identity": "#lab-identity-content",
        "section-lab-characteristics": "#lab-characteristics-content",
        "tab-lab-planning": "#lab-planning-content",
        "tab-lab-vf": "#lab-vf-content",
        "section-lab-specialties": "#lab-specialties-content",
        "section-lab-features": "#lab-features-content",
        "section-lab-rooms": "#lab-rooms-content",
        "section-lab-raw-vis": "#lab-raw-vis-content",
        "section-lab-items": "#lab-items-content",
        "tab-lab-diary": "#lab-diary-content",
    }
    _SECTION_TEXT: ClassVar[dict[str, str]] = {
        "section-lab-identity": "_identity_text",
        "section-lab-characteristics": "_characteristics_table_text",
        "tab-lab-planning": "_planning_text",
        "tab-lab-vf": "_vf_text",
        "section-lab-specialties": "_specialties_text",
        "section-lab-features": "_features_text",
        "section-lab-rooms": "_rooms_text",
        "section-lab-raw-vis": "_raw_vis_text",
        "section-lab-items": "_items_text",
        "tab-lab-diary": "_diary_text",
    }

    def refresh_section(self, section_id: str) -> None:
        selector = self._SECTION_CONTENT.get(section_id)
        text_method = self._SECTION_TEXT.get(section_id)
        if selector is None or text_method is None:
            return
        try:
            static = self.query_one(selector, Static)
        except NoMatches:
            return
        static.update(getattr(self, text_method)())
        if section_id == "section-lab-characteristics":
            # Two-column section: the derived stats sit in a sibling Static.
            self.query_one("#lab-characteristics-derived", Static).update(
                self._characteristics_derived_text()
            )

    def _identity_text(self) -> str:
        saga, lab = self.saga, self.laboratory
        covenant = saga.covenant(lab.covenant_id)
        owner = saga.character(lab.owner_id)
        # Inherited from the covenant, including any Boons that raise it.
        covenant_aura = (
            covenant_effective_aura(
                covenant, catalog.load_covenant_boon_hook_catalog_by_id()
            )
            if covenant
            else 0
        )
        return "\n".join(
            [
                f"Name: {escape(lab.name)}",
                f"Location: {escape(lab.location) or '(not set)'}",
                f"Points: {lab.build_points}",
                f"Owner: {escape(owner.name) if owner else '(unassigned)'}",
                f"Covenant: {escape(covenant.name) if covenant else '(none)'}",
                f"Aura: {covenant_aura} (covenant) {lab.aura_modifier:+d} (modifier) "
                f"= {lab_aura_total(lab, covenant_aura)}",
            ]
        )

    def _characteristics_derived_text(self) -> str:
        lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
        lab = self.laboratory
        rows = [
            ("Occupied Size:", lab_occupied_size(lab, lab_catalog)),
            ("Free Virtues:", lab_free_virtues(lab, lab_catalog)),
            ("Base Safety:", lab_base_safety(lab, lab_catalog)),
        ]
        width = max(len(label) for label, _ in rows)
        return "\n".join(
            f"{label:<{width}} {_sign_colored(value, f'{value:g}')}"
            for label, value in rows
        )

    def _characteristics_table_text(self) -> str:
        """The 8 Characteristics as an aligned table: manual value, the
        summed Virtue+Flaw modifier, and the total after '='. Every number
        is coloured by sign (see _sign_colored())."""
        lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
        lab = self.laboratory
        rows = []
        for characteristic in LAB_CHARACTERISTICS:
            manual, virtue_sum, flaw_sum, total = lab_characteristic_total(
                lab, lab_catalog, characteristic
            )
            label = characteristic.replace("_", " ").title() + ":"
            rows.append((label, manual, virtue_sum + flaw_sum, total))
        label_width = max(len(label) for label, *_ in rows)
        num_width = max(
            len(f"{value:+d}")
            for _, manual, vf, total in rows
            for value in (manual, vf, total)
        )

        def cell(value: int) -> str:
            return _sign_colored(value, f"{value:>+{num_width}d}")

        return "\n".join(
            f"{label:<{label_width}} {cell(manual)} {cell(vf)} = {cell(total)}"
            for label, manual, vf, total in rows
        )

    def _planning_text(self) -> str:
        return "Lab activity planning isn't built yet -- coming in a future update."

    def _vf_text(self) -> str:
        if not self.laboratory.virtues_flaws:
            return "(none recorded)"

        lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
        lines: list[str] = []
        for vf_type in ("Virtue", "Flaw"):
            entries = [
                vf
                for vf in self.laboratory.virtues_flaws
                if (definition := lab_catalog.get(vf.vf_id)) is not None
                and definition.type == vf_type
            ]
            if not entries:
                continue
            lines.append(f"{vf_type}s:")
            for vf in entries:
                definition = lab_catalog.get(vf.vf_id)
                tier = definition.tier if definition is not None else "?"
                lines.append(
                    f"  {escape(catalog.describe_virtue_flaw(vf, lab_catalog))} "
                    f"({tier})"
                )
            lines.append("")
        return "\n".join(lines).rstrip()

    def _specialties_text(self) -> str:
        if not self.laboratory.specialties:
            return "(none recorded)"
        return "\n".join(f"  - {escape(s)}" for s in self.laboratory.specialties)

    def _features_text(self) -> str:
        if not self.laboratory.features:
            return "(none recorded)"
        return "\n".join(f"  - {escape(f)}" for f in self.laboratory.features)

    def _rooms_text(self) -> str:
        if not self.laboratory.rooms:
            return "(none recorded)"
        return "\n".join(
            f"  {escape(room.name)}: {escape(room.description) or '(no description)'}"
            for room in self.laboratory.rooms
        )

    def _raw_vis_text(self) -> str:
        if not self.laboratory.raw_vis:
            return "(none recorded)"
        return "\n".join(
            f"{art.title()}: {pawns} pawn(s)"
            for art, pawns in sorted(self.laboratory.raw_vis.items())
        )

    def _items_text(self) -> str:
        if not self.laboratory.inventory_items:
            return "(none recorded)"
        return "\n".join(
            f"  {escape(item.name)}: {escape(item.description) or '(no description)'}"
            for item in self.laboratory.inventory_items
        )

    def _diary_text(self) -> str:
        if not self.laboratory.diary:
            return "(none recorded)"
        lines = []
        for entry in self.laboratory.diary:
            lines.append(f"{entry.year} {entry.season} -- {escape(entry.name)}")
            if entry.details:
                lines.append(f"  {escape(entry.details)}")
        return "\n".join(lines)


class FamiliarSheetView(Vertical):
    """The Familiar sheet mounted into WorkspaceScreen's detail pane.

    A fixed top panel (Familiar Info -- not inside any tab, permanently
    expanded, same PinnedCollapsible pattern as the other sheets) above a
    5-tab body mirroring reference/familiar-rules-and-sheet.md: Identity &
    Cords (Binding & Cords, Virtues & Flaws, Personality Traits &
    Reputations), Characteristics (the 8 Characteristics plus the typed-in
    Base Soak/Magic Resistance figures) and Combat & Health (Wounds/Fatigue,
    reusing Character's own dialogs; Natural Weapons & Attacks, a free
    selectable list of weapon-kind Possessions -- same shape as Character's
    weapon rows, see STORY-205), Abilities and Bond Powers.
    """

    DEFAULT_CSS = """
    FamiliarSheetView {
        height: 1fr;
    }

    FamiliarSheetView #fam-top-panel {
        width: 1fr;
        height: auto;
    }

    FamiliarSheetView TabbedContent {
        height: 1fr;
    }

    FamiliarSheetView TabPane {
        padding: 1 0;
    }

    FamiliarSheetView VerticalScroll {
        height: 1fr;
        width: 1fr;
    }

    FamiliarSheetView #fam-vf-row, FamiliarSheetView #fam-pt-rep-row,
    FamiliarSheetView #fam-health-row {
        width: 1fr;
        height: auto;
    }

    FamiliarSheetView #fam-health-wounds-col,
    FamiliarSheetView #fam-health-fatigue-col {
        width: 1fr;
        height: auto;
    }
    """

    def __init__(self, saga: Saga, familiar: Familiar) -> None:
        super().__init__()
        self.saga = saga
        self.familiar = familiar
        #: Set once TabbedContent's initial TabActivated has been seen -- see
        #: WorkspaceScreen.on_tabbed_content_tab_activated().
        self.initial_tab_seen = False

    def compose(self) -> ComposeResult:
        with (
            Vertical(id="fam-top-panel"),
            PinnedCollapsible(title="Familiar Info", id="section-fam-info"),
        ):
            yield Static(
                fam.identity_text(self.saga, self.familiar), id="fam-info-content"
            )
            yield Button("Edit (e)", id="btn-fam-info-edit", compact=True)
        with TabbedContent(initial="tab-fam-identity"):
            with TabPane("Identity & Cords", id="tab-fam-identity"), VerticalScroll():
                with SheetSection(title="Binding & Cords", id="section-fam-binding"):
                    yield Static(self._binding_text(), id="fam-binding-content")
                with Horizontal(id="fam-vf-row"):
                    with SheetSection(title="Virtues", id="section-fam-vf-virtues"):
                        yield SelectableList(
                            fam.vf_rows(self.familiar, "Virtue"),
                            id="fam-vf-virtues-list",
                        )
                    with SheetSection(title="Flaws", id="section-fam-vf-flaws"):
                        yield SelectableList(
                            fam.vf_rows(self.familiar, "Flaw"), id="fam-vf-flaws-list"
                        )
                yield Static(fam.vf_info_text(self.familiar, None), id="fam-vf-info")
                with Horizontal(id="fam-pt-rep-row"):
                    with SheetSection(
                        title="Personality Traits", id="section-fam-personality-traits"
                    ):
                        yield SelectableList(
                            fam.personality_trait_rows(self.familiar),
                            id="fam-personality-traits-list",
                        )
                    with SheetSection(
                        title="Reputations", id="section-fam-reputations"
                    ):
                        yield SelectableList(
                            fam.reputation_rows(self.familiar),
                            id="fam-reputations-list",
                        )
            with (
                TabPane("Characteristics", id="tab-fam-characteristics"),
                SheetSection(title="Characteristics", id="section-fam-characteristics"),
            ):
                yield Static(
                    fam.characteristics_text(self.familiar),
                    id="fam-characteristics-content",
                )
            with TabPane("Combat & Health", id="tab-fam-combat"), VerticalScroll():
                with (
                    SheetSection(title="Health", id="section-fam-health"),
                    Horizontal(id="fam-health-row"),
                ):
                    with Vertical(id="fam-health-wounds-col"):
                        yield Static(
                            fam.wounds_text(self.familiar), id="fam-wounds-content"
                        )
                        yield Button(
                            "Edit Wounds (e)",
                            id="btn-fam-health-wounds-edit",
                            compact=True,
                        )
                    with Vertical(id="fam-health-fatigue-col"):
                        yield Static(
                            fam.fatigue_text(self.familiar), id="fam-fatigue-content"
                        )
                        yield Button(
                            "Edit Fatigue",
                            id="btn-fam-health-fatigue-edit",
                            compact=True,
                        )
                with SheetSection(
                    title="Natural Weapons & Attacks",
                    id="section-fam-natural-weapons",
                ):
                    yield SelectableList(
                        fam.natural_weapon_rows(self.familiar),
                        id="fam-natural-weapons-list",
                    )
                    yield Static(
                        fam.natural_weapon_info_text(self.familiar, None),
                        id="fam-natural-weapons-info",
                    )
            with TabPane("Abilities", id="tab-fam-abilities"), VerticalScroll():
                yield Static(
                    "[dim]Languages: shares the Magus partner's Language "
                    "scores automatically.[/]"
                )
                yield SelectableList(
                    fam.ability_rows(self.familiar), id="fam-abilities-list"
                )
                yield Static(
                    fam.ability_info_text(self.familiar, None), id="fam-ability-info"
                )
            with TabPane("Bond Powers", id="tab-fam-powers"), VerticalScroll():
                yield SelectableList(
                    fam.bond_power_rows(self.familiar), id="fam-bond-powers-list"
                )
                yield Static(
                    fam.bond_power_info_text(self.familiar, None),
                    id="fam-bond-powers-info",
                )

    def _binding_text(self) -> str:
        return f"{fam.binding_text(self.familiar)}\n\n{fam.cords_text(self.familiar)}"

    def refresh_section(self, section_id: str) -> None:
        try:
            if section_id == "section-fam-info":
                self.query_one("#fam-info-content", Static).update(
                    fam.identity_text(self.saga, self.familiar)
                )
            elif section_id == "section-fam-binding":
                self.query_one("#fam-binding-content", Static).update(
                    self._binding_text()
                )
            elif section_id in ("section-fam-vf-virtues", "section-fam-vf-flaws"):
                self.query_one("#fam-vf-virtues-list", SelectableList).set_rows(
                    fam.vf_rows(self.familiar, "Virtue")
                )
                self.query_one("#fam-vf-flaws-list", SelectableList).set_rows(
                    fam.vf_rows(self.familiar, "Flaw")
                )
                self.query_one("#fam-vf-info", Static).update(
                    fam.vf_info_text(self.familiar, None)
                )
            elif section_id == "section-fam-personality-traits":
                self.query_one("#fam-personality-traits-list", SelectableList).set_rows(
                    fam.personality_trait_rows(self.familiar)
                )
            elif section_id == "section-fam-reputations":
                self.query_one("#fam-reputations-list", SelectableList).set_rows(
                    fam.reputation_rows(self.familiar)
                )
            elif section_id == "section-fam-characteristics":
                self.query_one("#fam-characteristics-content", Static).update(
                    fam.characteristics_text(self.familiar)
                )
            elif section_id == "section-fam-health":
                self.query_one("#fam-wounds-content", Static).update(
                    fam.wounds_text(self.familiar)
                )
                self.query_one("#fam-fatigue-content", Static).update(
                    fam.fatigue_text(self.familiar)
                )
            elif section_id == "section-fam-natural-weapons":
                self.query_one("#fam-natural-weapons-list", SelectableList).set_rows(
                    fam.natural_weapon_rows(self.familiar)
                )
                self.query_one("#fam-natural-weapons-info", Static).update(
                    fam.natural_weapon_info_text(self.familiar, None)
                )
            elif section_id == "tab-fam-abilities":
                self.query_one("#fam-abilities-list", SelectableList).set_rows(
                    fam.ability_rows(self.familiar)
                )
                self.query_one("#fam-ability-info", Static).update(
                    fam.ability_info_text(self.familiar, None)
                )
            elif section_id == "tab-fam-powers":
                self.query_one("#fam-bond-powers-list", SelectableList).set_rows(
                    fam.bond_power_rows(self.familiar)
                )
                self.query_one("#fam-bond-powers-info", Static).update(
                    fam.bond_power_info_text(self.familiar, None)
                )
        except NoMatches:
            pass

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
        other = (
            "fam-vf-flaws-list"
            if list_id == "fam-vf-virtues-list"
            else "fam-vf-virtues-list"
        )
        self.query_one(f"#{other}", SelectableList).clear_selection()
        self.query_one("#fam-vf-info", Static).update(
            fam.vf_info_text(self.familiar, event.data_index)
        )


class CovenantSheetView(Vertical):
    """The covenant sheet mounted into WorkspaceScreen's detail pane.

    A permanent info panel (not inside any tab) above six tabs mirroring
    the covenant record sheet: Attributes, Inhabitants, Possessions,
    Economics, Library, Diary (still a placeholder).

    The panel's saga-level values (Saga, Storyguide, Current Season,
    Current Year) are inherited from the Saga and shown dimmed/read-only;
    the rest belong to the covenant and are edited with 'e'.
    """

    DEFAULT_CSS = """
    CovenantSheetView {
        height: 1fr;
    }

    CovenantSheetView #cov-info-body {
        width: 1fr;
        height: auto;
    }

    CovenantSheetView #cov-info-left {
        width: 1fr;
        height: auto;
        margin-right: 4;
    }

    CovenantSheetView #cov-info-right {
        width: 1fr;
        height: auto;
    }

    CovenantSheetView TabbedContent {
        height: 1fr;
    }

    CovenantSheetView TabPane {
        padding: 1 0;
    }

    CovenantSheetView VerticalScroll {
        height: 1fr;
        width: 1fr;
    }

    CovenantSheetView #cov-bh-row {
        width: 1fr;
        height: auto;
    }

    CovenantSheetView #section-cov-boons {
        margin-right: 2;
    }

    CovenantSheetView #inh-body {
        height: 1fr;
    }

    CovenantSheetView #inh-loyalty-body,
    CovenantSheetView #inh-misc-body {
        width: 1fr;
        height: auto;
    }

    CovenantSheetView #inh-loyalty-left,
    CovenantSheetView #inh-misc-left {
        width: 1fr;
        height: auto;
        margin-right: 4;
    }

    CovenantSheetView #inh-loyalty-right,
    CovenantSheetView #inh-misc-right {
        width: 1fr;
        height: auto;
    }

    CovenantSheetView #inh-panel {
        width: 1fr;
        height: auto;
        min-height: 6;
        max-height: 14;
        margin-top: 1;
        padding: 1 2;
        background: $panel;
    }

    CovenantSheetView #pos-body {
        height: 1fr;
    }

    CovenantSheetView #pos-panel {
        width: 1fr;
        height: auto;
        min-height: 6;
        max-height: 14;
        margin-top: 1;
        padding: 1 2;
        background: $panel;
    }

    CovenantSheetView #eco-body {
        height: 1fr;
    }

    CovenantSheetView #eco-wealth-body {
        width: 1fr;
        height: auto;
    }

    CovenantSheetView #eco-wealth-left {
        width: 1fr;
        height: auto;
        margin-right: 4;
    }

    CovenantSheetView #eco-wealth-right {
        width: 1fr;
        height: auto;
    }

    CovenantSheetView .eco-header {
        width: 1fr;
        height: auto;
        color: $text-muted;
    }

    CovenantSheetView .inh-header {
        width: 1fr;
        height: auto;
        color: $text-muted;
    }

    CovenantSheetView .pos-header {
        width: 1fr;
        height: auto;
        color: $text-muted;
    }

    CovenantSheetView #eco-panel {
        width: 1fr;
        height: auto;
        min-height: 6;
        max-height: 14;
        margin-top: 1;
        padding: 1 2;
        background: $panel;
    }

    CovenantSheetView #cov-bh-info {
        width: 1fr;
        height: auto;
        min-height: 8;
        margin-top: 1;
        padding: 1 2;
        background: $panel;
    }
    """

    def __init__(self, saga: Saga, covenant: Covenant) -> None:
        super().__init__()
        self.saga = saga
        self.covenant = covenant
        #: Set once TabbedContent's initial TabActivated has been seen -- see
        #: WorkspaceScreen.on_tabbed_content_tab_activated().
        self.initial_tab_seen = False

    def compose(self) -> ComposeResult:
        with PinnedCollapsible(title=escape(self.covenant.name), id="section-cov-info"):
            with Horizontal(id="cov-info-body"):
                yield Static(self._info_left_text(), id="cov-info-left")
                yield Static(self._info_right_text(), id="cov-info-right")
            yield Button("Edit (e)", id="btn-cov-edit", compact=True)
        with TabbedContent(initial="tab-cov-attributes"):
            with TabPane("Attributes", id="tab-cov-attributes"), VerticalScroll():
                with SheetSection(title="Description", id="section-cov-description"):
                    yield Static(self._description_text(), id="cov-description-content")
                with SheetSection(title="Reputations", id="section-cov-reputations"):
                    yield SelectableList(
                        self._reputation_rows(), id="cov-reputations-list"
                    )
                with Horizontal(id="cov-bh-row"):
                    with SheetSection(
                        title=self._bh_title("Boon"), id="section-cov-boons"
                    ):
                        yield SelectableList(
                            self._bh_entries("Boon"), id="cov-boons-list"
                        )
                    with SheetSection(
                        title=self._bh_title("Hook"), id="section-cov-hooks"
                    ):
                        yield SelectableList(
                            self._bh_entries("Hook"), id="cov-hooks-list"
                        )
                yield Static(self._bh_info_text(None), id="cov-bh-info")
            with TabPane("Inhabitants", id="tab-cov-inhabitants"):
                yield from self._inhabitants_tab()
            with TabPane("Possessions", id="tab-cov-possessions"):
                yield from self._possessions_tab()
            with TabPane("Economics", id="tab-cov-economics"):
                yield from self._economics_tab()
            with TabPane("Library", id="tab-cov-library"):
                yield BookListView(
                    self.saga,
                    lambda: bk.books_in_covenant(self.saga, self.covenant),
                    section_id="section-lib-books",
                    summary=True,
                )
            with TabPane("Diary", id="tab-cov-diary"):
                yield Static(_tab_placeholder("Diary"))

    def _inhabitants_tab(self) -> ComposeResult:
        """Loyalty, the Inhabitants summary and Miscellaneous blocks, one
        collapsible list per kind of inhabitant, and (docked below the
        scrolling part) the details panel of the chosen inhabitant."""
        covenant, saga = self.covenant, self.saga
        with Vertical(id="inh-body"):
            with VerticalScroll(id="inh-scroll"):
                with (
                    SheetSection(title="Loyalty", id="section-inh-loyalty"),
                    Horizontal(id="inh-loyalty-body"),
                ):
                    yield Static(
                        inh.loyalty_left_text(saga, covenant), id="inh-loyalty-left"
                    )
                    yield Static(
                        inh.loyalty_right_text(saga, covenant), id="inh-loyalty-right"
                    )
                with SheetSection(title="Inhabitants", id="section-inh-population"):
                    yield Static(
                        inh.population_text(saga, covenant), id="inh-population-content"
                    )
                with SheetSection(title="Miscellaneous", id="section-inh-misc"):
                    left, right = inh.misc_text(covenant)
                    with Horizontal(id="inh-misc-body"):
                        yield Static(left, id="inh-misc-left")
                        yield Static(right, id="inh-misc-right")
                for kind in INHABITANT_KINDS:
                    with SheetSection(
                        title=self._inh_title(kind), id=f"section-inh-{kind}"
                    ):
                        yield Static(inh.table_header(kind), classes="inh-header")
                        yield SelectableList(
                            self._inh_rows(kind), id=f"inh-{kind}-list"
                        )
            yield Static(inh.detail_text(None, saga.current_year), id="inh-panel")

    def _possessions_tab(self) -> ComposeResult:
        """One collapsible list per kind of possession over the details panel of
        the chosen one (docked below the scrolling part)."""
        with Vertical(id="pos-body"):
            with VerticalScroll(id="pos-scroll"):
                for kind in POSSESSION_KINDS:
                    with SheetSection(
                        title=pos.KIND_TITLES[kind], id=f"section-pos-{kind}"
                    ):
                        yield Static(pos.table_header(kind), classes="pos-header")
                        yield SelectableList(
                            self._pos_rows(kind), id=f"pos-{kind}-list"
                        )
            yield Static(pos.detail_text(None), id="pos-panel")

    #: The three lists of the Economics tab (one selection across them).
    _ECO_LISTS: ClassVar[tuple[str, ...]] = ("income", "expenditure", "savings")

    def _economics_tab(self) -> ComposeResult:
        """Wealth, Sources of Income, Yearly Expenditure and Cost Savings over
        the details panel of the chosen row (docked below the scrolling part)."""
        summary = eco.summarize(self.saga, self.covenant)
        left, right = eco.wealth_texts(summary)
        with Vertical(id="eco-body"):
            with VerticalScroll(id="eco-scroll"):
                with (
                    SheetSection(title="Wealth", id="section-eco-wealth"),
                    Horizontal(id="eco-wealth-body"),
                ):
                    yield Static(left, id="eco-wealth-left")
                    yield Static(right, id="eco-wealth-right")
                with SheetSection(title="Sources of Income", id="section-eco-income"):
                    yield Static(eco.source_table_header(), classes="eco-header")
                    yield SelectableList(
                        self._eco_rows("income", summary), id="eco-income-list"
                    )
                with SheetSection(
                    title="Yearly Expenditure", id="section-eco-expenditure"
                ):
                    yield Static(eco.table_header("Cost"), classes="eco-header")
                    yield SelectableList(
                        self._eco_rows("expenditure", summary),
                        id="eco-expenditure-list",
                    )
                with SheetSection(title="Cost Savings", id="section-eco-savings"):
                    yield Static(eco.table_header("Quantity"), classes="eco-header")
                    yield SelectableList(
                        self._eco_rows("savings", summary), id="eco-savings-list"
                    )
            yield Static(eco.source_detail_text(None), id="eco-panel")

    def _eco_rows(self, which: str, summary: eco.Summary) -> list[tuple[int, str]]:
        if which == "income":
            sources = self.covenant.economics.income_sources
            return [(i, eco.source_row_label(s)) for i, s in enumerate(sources)]
        rows = summary.expenditure if which == "expenditure" else summary.savings
        return [(i, eco.row_label(row)) for i, row in enumerate(rows)]

    def selected_economics(self, which: str) -> int | None:
        """Index of the chosen row of the `which` list ("income" indexes the
        covenant's income sources; the others index the summary's rows)."""
        return self.query_one(f"#eco-{which}-list", SelectableList).selected_data_index

    def _eco_panel_text(self, which: str, index: int, summary: eco.Summary) -> str:
        if which == "income":
            sources = self.covenant.economics.income_sources
            return eco.source_detail_text(
                sources[index] if index < len(sources) else None
            )
        rows = summary.expenditure if which == "expenditure" else summary.savings
        first = "Cost" if which == "expenditure" else "Quantity"
        return eco.row_detail_text(rows[index] if index < len(rows) else None, first)

    def _rebuild_economics(self) -> None:
        """Recalculate everything on the tab. Anything on the sheet can move a
        figure (a new inhabitant, a laboratory's usage, the salary), so this
        also runs after edits made on other tabs. The chosen row stays chosen
        and its panel is refreshed."""
        summary = eco.summarize(self.saga, self.covenant)
        left, right = eco.wealth_texts(summary)
        self.query_one("#eco-wealth-left", Static).update(left)
        self.query_one("#eco-wealth-right", Static).update(right)
        any_chosen = False
        for which in self._ECO_LISTS:
            rows_list = self.query_one(f"#eco-{which}-list", SelectableList)
            chosen = rows_list.selected_data_index
            rows_list.set_rows(self._eco_rows(which, summary))
            if chosen is not None and chosen < len(rows_list._rows):
                any_chosen = True
                rows_list.highlighted = chosen  # posts Chosen -> refreshes the panel
        if not any_chosen:
            self.query_one("#eco-panel", Static).update(eco.source_detail_text(None))

    def _pos_entries(self, kind: str) -> list[pos.PossessionEntry]:
        return pos.entries_for_kind(
            self.saga, self.covenant, kind, catalog.load_lab_virtue_flaw_catalog_by_id()
        )

    def _pos_rows(self, kind: str) -> list[tuple[int, str]]:
        return [(i, pos.row_label(e)) for i, e in enumerate(self._pos_entries(kind))]

    def selected_possession(self, kind: str) -> int | None:
        """Index into the `kind` list's entries of the chosen row, or None."""
        return self.query_one(f"#pos-{kind}-list", SelectableList).selected_data_index

    def _rebuild_possessions(self) -> None:
        """Re-render every list and reset the panel."""
        for kind in POSSESSION_KINDS:
            self.query_one(f"#pos-{kind}-list", SelectableList).set_rows(
                self._pos_rows(kind)
            )
        self.query_one("#pos-panel", Static).update(pos.detail_text(None))

    def _inh_entries(self, kind: str) -> list[inh.InhabitantEntry]:
        return inh.entries_for_kind(self.saga, self.covenant, kind)

    def _inh_rows(self, kind: str) -> list[tuple[int, str]]:
        return [(i, inh.row_label(e)) for i, e in enumerate(self._inh_entries(kind))]

    def _inh_title(self, kind: str) -> str:
        """ "Magi (1)": the list's headcount -- quantities added up."""
        return f"{inh.KIND_TITLES[kind]} ({inh.headcount(self._inh_entries(kind))})"

    def selected_inhabitant(self, kind: str) -> int | None:
        """Index into the `kind` list's entries of the chosen row, or None."""
        return self.query_one(f"#inh-{kind}-list", SelectableList).selected_data_index

    def _rebuild_inhabitants(self) -> None:
        """Re-render every list, its title, the population total and the panel
        (any change can move the headcounts and the calculated total)."""
        for kind in INHABITANT_KINDS:
            self._set_section_title(
                self.query_one(f"#section-inh-{kind}", Collapsible),
                self._inh_title(kind),
            )
            self.query_one(f"#inh-{kind}-list", SelectableList).set_rows(
                self._inh_rows(kind)
            )
        self.query_one("#inh-population-content", Static).update(
            inh.population_text(self.saga, self.covenant)
        )
        self.query_one("#inh-panel", Static).update(
            inh.detail_text(None, self.saga.current_year)
        )

    def refresh_section(self, section_id: str) -> None:
        try:
            self._refresh_section(section_id)
            if section_id.startswith(("section-inh-", "section-pos-", "section-cov-")):
                # These feed the Economics tab's figures.
                self._rebuild_economics()
            if section_id in ("section-cov-info", "section-cov-reputations") or (
                section_id.startswith("section-inh-")
                and section_id != "section-inh-loyalty"
            ):
                # Magi (Gift), Specialists/Companions (role bonus), covenant
                # Reputations and Living Conditions (Mundane) all feed the
                # Loyalty block, which lives on a different section.
                self._refresh_loyalty_text()
        except NoMatches:
            # The sheet is being replaced or torn down (a refresh from a
            # dialog callback can land after that) -- nothing left to update.
            return

    def _refresh_loyalty_text(self) -> None:
        self.query_one("#inh-loyalty-left", Static).update(
            inh.loyalty_left_text(self.saga, self.covenant)
        )
        self.query_one("#inh-loyalty-right", Static).update(
            inh.loyalty_right_text(self.saga, self.covenant)
        )

    def _refresh_section(self, section_id: str) -> None:
        if section_id == "section-cov-info":
            self.query_one("#section-cov-info", Collapsible).title = escape(
                self.covenant.name
            )
            self.query_one("#cov-info-left", Static).update(self._info_left_text())
            self.query_one("#cov-info-right", Static).update(self._info_right_text())
        elif section_id == "section-cov-description":
            self.query_one("#cov-description-content", Static).update(
                self._description_text()
            )
        elif section_id == "section-cov-reputations":
            self.query_one("#cov-reputations-list", SelectableList).set_rows(
                self._reputation_rows()
            )
        elif section_id == "section-inh-loyalty":
            self._refresh_loyalty_text()
        elif section_id in ("section-inh-population", "section-inh-misc"):
            self.query_one("#inh-population-content", Static).update(
                inh.population_text(self.saga, self.covenant)
            )
            left, right = inh.misc_text(self.covenant)
            self.query_one("#inh-misc-left", Static).update(left)
            self.query_one("#inh-misc-right", Static).update(right)
        elif section_id.startswith("section-inh-"):
            self._rebuild_inhabitants()
        elif section_id.startswith("section-pos-"):
            self._rebuild_possessions()
        elif section_id.startswith("section-eco-"):
            self._rebuild_economics()
        elif section_id in ("section-cov-boons", "section-cov-hooks"):
            self._rebuild_boons_hooks()
            # An Aura Boon changes the Aura shown in the info panel.
            self.refresh_section("section-cov-info")

    def _rebuild_boons_hooks(self) -> None:
        """Re-render both lists, both titles and the details panel. Always
        both: the two titles share one colour driven by comparing the totals,
        so a change to either kind can change the other's title too."""
        for kind in ("Boon", "Hook"):
            self._set_section_title(
                self.query_one(f"#section-cov-{kind.lower()}s", Collapsible),
                self._bh_title(kind),
            )
            self.query_one(f"#cov-{kind.lower()}s-list", SelectableList).set_rows(
                self._bh_entries(kind)
            )
        self.query_one("#cov-bh-info", Static).update(self._bh_info_text(None))

    def selected_boon_hook(self, kind: str) -> int | None:
        """Index into covenant.boons_hooks of the row currently selected in
        the `kind` ("Boon"/"Hook") list, or None if none is."""
        return self.query_one(
            f"#cov-{kind.lower()}s-list", SelectableList
        ).selected_data_index

    def selected_reputation(self) -> int | None:
        """Index into covenant.reputations of the chosen row, or None."""
        return self.query_one(
            "#cov-reputations-list", SelectableList
        ).selected_data_index

    @staticmethod
    def _set_section_title(section: Collapsible, title: str) -> None:
        """Set a section's title, forcing the label to repaint. Textual's
        Content compares equal on plain text alone, so a colour-only change
        (Hooks (7 pts) turning red) would otherwise leave the old colour
        showing."""
        section.title = title
        title_widget = section.query_one(CollapsibleTitle)
        # The label reactive skips "unchanged" values too, so store the new
        # Content directly (set_reactive bypasses that check), then repaint.
        title_widget.set_reactive(type(title_widget).label, Content.from_text(title))
        title_widget._update_label()

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        """A Boon or Hook row was chosen: fill the details panel. (Reputations
        have no panel -- a name and a score have nothing more to show.)"""
        list_id = event.selectable_list.id or ""
        if list_id.startswith("eco-") and list_id.endswith("-list"):
            event.stop()
            which = list_id[len("eco-") : -len("-list")]
            for other in self._ECO_LISTS:  # one selection across the lists
                if other != which:
                    self.query_one(
                        f"#eco-{other}-list", SelectableList
                    ).clear_selection()
            self.query_one("#eco-panel", Static).update(
                self._eco_panel_text(
                    which, event.data_index, eco.summarize(self.saga, self.covenant)
                )
            )
            return
        if list_id.startswith("inh-") and list_id.endswith("-list"):
            event.stop()
            kind = list_id[len("inh-") : -len("-list")]
            # One selection across all the inhabitant lists.
            for other in INHABITANT_KINDS:
                if other != kind:
                    self.query_one(
                        f"#inh-{other}-list", SelectableList
                    ).clear_selection()
            entries = self._inh_entries(kind)
            chosen = (
                entries[event.data_index] if event.data_index < len(entries) else None
            )
            self.query_one("#inh-panel", Static).update(
                inh.detail_text(chosen, self.saga.current_year)
            )
            return
        if list_id.startswith("pos-") and list_id.endswith("-list"):
            event.stop()
            kind = list_id[len("pos-") : -len("-list")]
            for other in POSSESSION_KINDS:  # one selection across the lists
                if other != kind:
                    self.query_one(
                        f"#pos-{other}-list", SelectableList
                    ).clear_selection()
            entries = self._pos_entries(kind)
            chosen = (
                entries[event.data_index] if event.data_index < len(entries) else None
            )
            self.query_one("#pos-panel", Static).update(pos.detail_text(chosen))
            return
        if list_id not in ("cov-boons-list", "cov-hooks-list"):
            return
        event.stop()
        # One selection across both lists: unchoose the other one.
        other = "cov-hooks-list" if list_id == "cov-boons-list" else "cov-boons-list"
        self.query_one(f"#{other}", SelectableList).clear_selection()
        self.query_one("#cov-bh-info", Static).update(
            self._bh_info_text(event.data_index)
        )

    @staticmethod
    def _inherited(value: str) -> str:
        """Dim a value that comes from the saga and isn't edited here."""
        return f"[dim]{escape(value)}[/]"

    def _aura_text(self) -> str:
        """The base Aura, plus where a Boon-raised total comes from."""
        cov = self.covenant
        effective = covenant_effective_aura(
            cov, catalog.load_covenant_boon_hook_catalog_by_id()
        )
        if effective == cov.aura:
            return str(cov.aura)
        return f"{effective} (base {cov.aura}, {effective - cov.aura:+d} Boons)"

    def _info_left_text(self) -> str:
        cov, saga = self.covenant, self.saga
        founded = "(not set)" if cov.year_founded is None else str(cov.year_founded)
        return aligned(
            [
                ("Saga", self._inherited(saga.name)),
                ("Storyguide", self._inherited(saga.storyguide or "(not set)")),
                ("Year Founded", founded),
                ("Aegis of the Hearth", str(cov.aegis_of_the_hearth)),
                ("Living Conditions (Magi)", str(cov.living_conditions_magi)),
                ("Aura", self._aura_text()),
            ]
        )

    def _info_right_text(self) -> str:
        cov, saga = self.covenant, self.saga
        return aligned(
            [
                ("Tribunal", escape(cov.tribunal) if cov.tribunal else "(not set)"),
                ("Current Season", self._inherited(saga.current_season)),
                ("Current Year", self._inherited(str(saga.current_year))),
                ("Aegis' Penetration", str(cov.aegis_penetration)),
                ("Living Conditions (Mundane)", str(cov.living_conditions_mundane)),
                ("Covenant Season", cov.covenant_season),
            ]
        )

    def _description_text(self) -> str:
        # Backed by Covenant.notes (the free-text field set at creation).
        text = self.covenant.notes.strip()
        return markdown_inline(text) if text else "(no description)"

    def _reputation_rows(self) -> list[tuple[int, str]]:
        """The covenant's Reputations as (index, label) rows. A bad Reputation
        the covenant doesn't know about is marked -- it doesn't count against
        Loyalty until it's known (see inhabitants.reputation_loyalty_penalty)."""
        return [
            (
                index,
                f"{escape(r.name)}: {r.score:+d}"
                + ("" if r.known else " [dim](not known by the covenant)[/]"),
            )
            for index, r in enumerate(self.covenant.reputations)
        ]

    def _bh_title(self, kind: str) -> str:
        """ "Boons (7 pts)" / "Hooks (7 pts)": Boons show the points they
        cost, Hooks the points they provide. The parenthesised total of BOTH
        titles takes one colour from comparing the two (see _balance_colour)."""
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        boons = covenant_boon_points(self.covenant, by_id)
        hooks = covenant_hook_points(self.covenant, by_id)
        points = boons if kind == "Boon" else hooks
        colour = _balance_colour(boons, hooks)
        unit = "pt" if points == 1 else "pts"
        return f"{kind}s [{colour}]({points:g} {unit})[/]"

    def _bh_entries(self, kind: str) -> list[tuple[int, str]]:
        """The attached Boons or Hooks of `kind` as (index into
        covenant.boons_hooks, display label) pairs, in attach order."""
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        return [
            (index, escape(catalog.describe_boon_hook(bh, by_id)))
            for index, bh in enumerate(self.covenant.boons_hooks)
            if bh.vf_id in by_id and by_id[bh.vf_id].type == kind
        ]

    def _bh_info_text(self, index: int | None) -> str:
        """The details panel for the attached Boon/Hook at `index` into
        covenant.boons_hooks: its name, type, notes, the user's own
        description (if any) and then the official rules text."""
        if index is None:
            return "[dim]Select a Boon or Hook to read its rules.[/]"
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        instance = self.covenant.boons_hooks[index]
        definition = by_id.get(instance.vf_id)
        if definition is None:
            return escape(f"{instance.vf_id} (not in catalog)")

        lines = [f"[b]Name:[/] {escape(catalog.describe_boon_hook(instance, by_id))}"]
        if definition.category:
            lines.append(f"[b]Type:[/] {definition.category}")
        lines.append(f"[b]Tier:[/] {_tier_text(definition)}")
        if definition.requires:
            lines.append(
                f"[b]Requires:[/] {_boon_hook_names(definition.requires, by_id)}"
            )
        if definition.excludes:
            lines.append(
                f"[b]Not with:[/] {_boon_hook_names(definition.excludes, by_id)}"
            )
        lines += st.effect_lines(definition.modifiers)
        if definition.repeatable:
            lines.append("[dim]May be taken more than once; the effects stack.[/]")
        # The user's own description leads; the official rules text follows.
        description = instance.params.get(BOON_HOOK_DESCRIPTION, "").strip()
        if description:
            lines += ["", "[b]Description:[/]", markdown_inline(description)]
        lines += ["", "[b]Rules:[/]", escape(definition.description)]
        return "\n".join(lines)


def _tree_node_with_data(tree: Tree, data: tuple) -> Any:
    """The first node of `tree` whose `.data` is `data`, or None."""
    pending = [tree.root]
    while pending:
        node = pending.pop()
        if node.data == data:
            return node
        pending.extend(node.children)
    return None


class WorkspaceScreen(Screen[None]):
    """Persistent nav tree (left) + detail pane (right) for one open saga.

    Replaces the old Saga -> Covenant -> Character/Lab/Library drill-down
    screens with a single workspace: the whole saga's structure is always
    visible in the tree, and selecting any node swaps the detail pane on
    the right, so comparing siblings doesn't mean popping all the way back
    up and down again.
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        ("n", "create_covenant", "New Covenant"),
        ("c", "create_character", "New Character"),
        ("l", "create_laboratory", "New Laboratory"),
        ("f", "create_familiar", "Bind Familiar"),
        ("a", "add", "Add"),
        ("A", "remove", "Remove"),
        ("e", "edit", "Edit"),
        ("r", "restore", "Restore"),
        ("i", "improve", "Improve"),
        ("I", "import_data", "Import"),
        ("t", "advance_season", "Advance Season"),
        ("T", "set_date", "Set Date"),
        ("v", "add_virtue_flaw", "Add Virtue/Flaw"),
        ("V", "remove_virtue_flaw", "Remove Virtue/Flaw"),
        ("escape", "app.pop_screen", "Back"),
        ("q", "quit", "Quit"),
    ]

    #: Covenant tabs that own their own a/A/e dispatch (keyed by tab id).
    #: None: every covenant tab's content is in Collapsible sections, so with
    #: nothing focused in one the dispatch falls back to the always-visible
    #: info panel. See _active_section().
    _COVENANT_DISPATCH_TABS: ClassVar[set[str]] = set()

    #: Character tabs that own their own a/A/e dispatch (keyed by tab id),
    #: same idea as _COVENANT_DISPATCH_TABS -- "tab-abilities" is a flat
    #: pane with no sub-sections, so it dispatches on its own tab id rather
    #: than falling back to the top panel. See _active_section().
    _CHARACTER_DISPATCH_TABS: ClassVar[set[str]] = {"tab-abilities"}

    #: Familiar tabs that own their own a/A/e dispatch (keyed by tab id),
    #: same idea as _CHARACTER_DISPATCH_TABS -- both are flat panes with no
    #: sub-sections. See _active_section().
    _FAMILIAR_DISPATCH_TABS: ClassVar[set[str]] = {
        "tab-fam-abilities",
        "tab-fam-powers",
    }

    #: Per sheet kind: the tabs that dispatch on their own id, and the
    #: section a tab with no focused section falls back to (None: the tab
    #: itself -- every Laboratory tab dispatches). See _active_section().
    _SHEET_DISPATCH: ClassVar[dict[str, tuple[set[str], str | None]]] = {
        "character": (_CHARACTER_DISPATCH_TABS, "section-char-info"),
        "laboratory": (set(), None),
        "covenant": (_COVENANT_DISPATCH_TABS, "section-cov-info"),
        "familiar": (_FAMILIAR_DISPATCH_TABS, "section-fam-info"),
    }

    DEFAULT_CSS = """
    #workspace-body {
        height: 1fr;
    }

    #nav-tree {
        width: 34;
        border-right: solid $accent;
    }

    #detail-pane {
        width: 1fr;
        padding: 1 2;
    }
    """

    def __init__(self, saga: Saga) -> None:
        super().__init__()
        self.saga = saga
        self.selected_kind: str = "saga"
        self.selected_covenant: Covenant | None = None
        self.selected_character: Character | None = None
        self.selected_laboratory: Laboratory | None = None
        self.selected_familiar: Familiar | None = None
        self._character_sheet_view: CharacterSheetView | None = None
        self._laboratory_sheet_view: LaboratorySheetView | None = None
        self._covenant_sheet_view: CovenantSheetView | None = None
        self._familiar_sheet_view: FamiliarSheetView | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="workspace-body"):
            yield Tree(escape(self.saga.name), data=("saga",), id="nav-tree")
            yield VerticalScroll(id="detail-pane")
        yield BottomBar()

    async def on_mount(self) -> None:
        self._update_saga_clock()
        self._rebuild_tree()
        await self._show_saga_detail()

    def _update_saga_clock(self) -> None:
        """Shows the saga's current date in the Header, on every screen of
        the workspace -- the saga owns the calendar, everything inherits it."""
        saga = self.saga
        self.sub_title = (
            f"{escape(saga.name)} | {saga.current_season} {saga.current_year}"
        )

    def _rebuild_tree(self) -> None:
        tree = self.query_one("#nav-tree", Tree)
        tree.reset(escape(self.saga.name), data=("saga",))
        tree.root.expand()

        for covenant in self.saga.covenants:
            cov_node = tree.root.add(
                escape(covenant.name), data=("covenant", covenant.id), expand=True
            )

            characters = [
                c for c in self.saga.characters if c.covenant_id == covenant.id
            ]
            char_group = cov_node.add(
                f"Characters ({len(characters)})",
                data=("character_group", covenant.id),
                expand=True,
            )
            for character in characters:
                self._add_character_node(char_group, character)

            labs = [
                lab for lab in self.saga.laboratories if lab.covenant_id == covenant.id
            ]
            lab_group = cov_node.add(
                f"Laboratories ({len(labs)})",
                data=("laboratory_group", covenant.id),
                expand=True,
            )
            for lab in labs:
                lab_group.add_leaf(escape(lab.name), data=("laboratory", lab.id))

        # Characters and labs with no (or a no-longer-existing) covenant live
        # directly under the saga -- assigning to a covenant is optional, and
        # this is where things land if they're taken out of one.
        covenant_ids = {c.id for c in self.saga.covenants}
        loose_characters = [
            c for c in self.saga.characters if c.covenant_id not in covenant_ids
        ]
        if loose_characters:
            group = tree.root.add(
                f"Unassigned Characters ({len(loose_characters)})",
                data=("character_group", None),
                expand=True,
            )
            for character in loose_characters:
                self._add_character_node(group, character)
        loose_labs = [
            lab for lab in self.saga.laboratories if lab.covenant_id not in covenant_ids
        ]
        if loose_labs:
            group = tree.root.add(
                f"Unassigned Laboratories ({len(loose_labs)})",
                data=("laboratory_group", None),
                expand=True,
            )
            for lab in loose_labs:
                group.add_leaf(escape(lab.name), data=("laboratory", lab.id))
        # Books with no owner file under the saga.
        loose_books = bk.unassigned_books(self.saga)
        if loose_books:
            tree.root.add_leaf(
                f"Unassigned Books ({len(loose_books)})", data=("book_group",)
            )
        tree.root.add_leaf(self._spells_label(), data=("spells",))

    def _add_character_node(self, parent, character: Character) -> None:
        """A character's own tree node: a plain leaf, unless it's a magus
        with a bound Familiar, in which case it becomes an expandable node
        with the Familiar as its one child leaf (nested under its creator,
        never its own group -- see kanban STORY-206)."""
        label = f"{escape(character.name)} ({character.type})"
        familiar = (
            fam.familiar_of(self.saga, character.id)
            if character.type == "magus"
            else None
        )
        if familiar is None:
            parent.add_leaf(label, data=("character", character.id))
            return
        node = parent.add(label, data=("character", character.id), expand=True)
        node.add_leaf(
            f"Familiar: {escape(familiar.name)}", data=("familiar", familiar.id)
        )

    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        data = event.node.data
        if data is None:
            return

        kind = data[0]
        self.selected_kind = kind
        self._character_sheet_view = None
        self._laboratory_sheet_view = None
        self._covenant_sheet_view = None
        self._familiar_sheet_view = None

        if kind == "saga":
            self.selected_covenant = None
            self.selected_character = None
            self.selected_laboratory = None
            self.selected_familiar = None
            await self._show_saga_detail()
        elif kind == "covenant":
            covenant = next(c for c in self.saga.covenants if c.id == data[1])
            self.selected_covenant = covenant
            self.selected_character = None
            self.selected_laboratory = None
            self.selected_familiar = None
            await self._show_covenant_detail(covenant)
        elif kind == "character_group":
            covenant = self.saga.covenant(data[1])
            self.selected_covenant = covenant
            self.selected_character = None
            await self._show_placeholder_detail(
                f"Characters in {covenant.name}"
                if covenant
                else "Unassigned Characters",
                "Select a character from the tree, or press 'c' to add one."
                if covenant
                else "These characters aren't assigned to a covenant. Select one "
                "from the tree, or press 'c' to add one.",
            )
        elif kind == "character":
            character = next(c for c in self.saga.characters if c.id == data[1])
            self.selected_character = character
            self.selected_covenant = self.saga.covenant(character.covenant_id)
            self.selected_familiar = None
            await self._show_character_detail(character)
        elif kind == "familiar":
            familiar = next(f for f in self.saga.familiars if f.id == data[1])
            self.selected_familiar = familiar
            self.selected_character = self.saga.character(familiar.character_id)
            self.selected_covenant = (
                self.saga.covenant(self.selected_character.covenant_id)
                if self.selected_character is not None
                else None
            )
            await self._show_familiar_detail(familiar)
        elif kind == "laboratory_group":
            covenant = self.saga.covenant(data[1])
            self.selected_covenant = covenant
            self.selected_laboratory = None
            await self._show_placeholder_detail(
                f"Laboratories in {covenant.name}"
                if covenant
                else "Unassigned Laboratories",
                "Select a laboratory from the tree, or press 'l' to add one."
                if covenant
                else "These laboratories aren't assigned to a covenant. Select "
                "one from the tree, or press 'l' to add one.",
            )
        elif kind == "laboratory":
            lab = next(lab for lab in self.saga.laboratories if lab.id == data[1])
            self.selected_laboratory = lab
            self.selected_covenant = self.saga.covenant(lab.covenant_id)
            await self._show_laboratory_detail(lab)
        elif kind == "spells":
            self.selected_covenant = None
            await self._set_detail(SpellListView(self.saga))
        elif kind == "book_group":
            self.selected_covenant = None
            await self._set_detail(
                BookListView(
                    self.saga,
                    lambda: bk.unassigned_books(self.saga),
                    section_id="section-unassigned-books",
                    title="Unassigned Books",
                )
            )

        self.refresh_bindings()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "create_covenant":
            return self.selected_kind == "saga"
        # Characters and labs may be created anywhere: a selected covenant
        # is just the default for the dialog's optional Covenant field.
        if action == "edit" and self.selected_kind == "saga":
            return True
        if action in ("add", "remove", "edit", "restore"):
            return self._section_op(action) is not None
        if action == "improve":
            return self._active_section() == "section-eco-income"
        if action == "import_data":
            return (
                self.selected_kind == "saga"
                or self._active_section() in _LIBRARY_SECTIONS
            )
        if action in ("add_virtue_flaw", "remove_virtue_flaw"):
            if self.selected_kind == "laboratory":
                return self._active_section() == "tab-lab-vf"
            if self.selected_kind == "familiar":
                return self._active_section() in (
                    "section-fam-vf-virtues",
                    "section-fam-vf-flaws",
                )
            return self._active_section() in ("section-vf-virtues", "section-vf-flaws")
        if action == "create_familiar":
            return bool(fam.unbonded_magi(self.saga))
        return True

    def _active_section(self) -> str | None:
        """Which sheet section is "active" for a/A/e (and v/V) dispatch: the
        nearest Collapsible around whatever has focus -- which also covers a
        sheet's top panel, outside its tabs. With none, a flat tab that
        dispatches on its own id (see _SHEET_DISPATCH), otherwise the sheet's
        always-visible top section, so 'e' edits the record from any tab.
        The Unassigned Books and Spells nodes have no sheet, just a section."""
        if self.selected_kind == "book_group":
            return "section-unassigned-books"
        if self.selected_kind == "spells":
            return SPELL_SECTION
        view = self._current_sheet_view()
        if view is None:
            return None
        try:
            tab_id = view.query_one(TabbedContent).active
        except NoMatches:
            return None
        if not tab_id:
            return None

        focused = self.app.focused
        if focused is not None:
            for widget in focused.ancestors_with_self:
                if isinstance(widget, Collapsible) and widget.id:
                    return widget.id
        own_tabs, fallback = self._SHEET_DISPATCH[self.selected_kind]
        return tab_id if fallback is None or tab_id in own_tabs else fallback

    def on_tabbed_content_tab_activated(
        self, event: TabbedContent.TabActivated
    ) -> None:
        # Keep the Footer's binding hints (and check_action gating) in sync
        # with whichever tab the user just switched to, and give the new
        # tab's first section focus so 'e'/'a'/'A' work immediately without
        # requiring an explicit Tab-key navigation first.
        view = self._current_sheet_view()
        initial = False
        if view is not None:
            # TabbedContent announces its initial tab once, right after
            # mounting. That's not a user tab switch, and treating it as one
            # would clear the focus _show_*_detail() just set.
            initial = not view.initial_tab_seen
            view.initial_tab_seen = True
        self._focus_first_section(initial=initial)
        self.refresh_bindings()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """The sheets' Edit buttons."""
        handler = {
            "btn-lab-identity-edit": self._edit_lab_identity,
            "btn-lab-characteristics-edit": self._edit_lab_characteristics,
            "btn-cov-edit": self._edit_covenant,
            "btn-char-info-edit": self._edit_character_info,
            "btn-char-characteristics-edit": self._edit_characteristics,
            "btn-char-health-wounds-edit": self._edit_wounds,
            "btn-char-health-fatigue-edit": self._edit_fatigue,
            "btn-fam-info-edit": self._edit_familiar_info,
            "btn-fam-health-wounds-edit": self._edit_familiar_wounds,
            "btn-fam-health-fatigue-edit": self._edit_familiar_fatigue,
        }.get(event.button.id or "")
        if handler is not None:
            event.stop()
            handler()

    def _focus_first_section(self, *, initial: bool = False) -> None:
        """Give the sheet a focused section, so 'e'/'a'/'A' work straight away.

        When a sheet is first shown (`initial`), focus its first section
        anywhere -- the always-visible top panel. On a later tab switch, focus
        that tab's first section, or clear focus for a flat tab: the top
        panel lives outside the tabs, so a tab switch never blurs it, and
        leaving it focused would make _active_section() keep reporting it.

        The Laboratory is the exception on first showing: its default tab
        (Planning) is flat, so it looks at the active tab first and only then
        falls back to the top panel."""
        view = self._current_sheet_view()
        if view is None:
            return
        active_tab_first = self.selected_kind == "laboratory"
        try:
            if initial and not active_tab_first:
                collapsible = view.query(Collapsible).first()
            else:
                tabbed = view.query_one(TabbedContent)
                if not tabbed.active:
                    return
                pane = view.query_one(f"#{tabbed.active}", TabPane)
                collapsible = pane.query(Collapsible).first()
        except NoMatches:
            if not initial:
                self.screen.set_focus(None)
                return
            if not active_tab_first:
                return
            try:
                collapsible = view.query(Collapsible).first()
            except NoMatches:
                return
        collapsible.query_one("CollapsibleTitle").focus()

    def on_descendant_focus(self, event: DescendantFocus) -> None:
        # Focus can move between Collapsible sections within the same tab
        # (no TabActivated message for that) -- keep bindings in sync then
        # too, or the Footer hint and check_action gating go stale.
        self.refresh_bindings()

    def on_descendant_blur(self, event: DescendantBlur) -> None:
        self.refresh_bindings()

    async def _set_detail(self, *widgets: Widget) -> None:
        detail_pane = self.query_one("#detail-pane", VerticalScroll)
        # Must be awaited before mounting replacements below, or a same-id
        # widget not yet removed collides with its freshly-mounted
        # replacement and Textual raises DuplicateIds.
        await detail_pane.remove_children()
        await detail_pane.mount(*widgets)

    async def _show_placeholder_detail(self, title: str, hint: str) -> None:
        await self._set_detail(Static(f"{title}\n\n{hint}"))

    async def _show_saga_detail(self) -> None:
        saga = self.saga
        lines = [
            f"Saga: {escape(saga.name)}",
            f"Storyguide: {escape(saga.storyguide)}",
            f"Current date: {saga.current_season} {saga.current_year}",
        ]
        if saga.description:
            lines.append(f"Description: {escape(saga.description)}")
        lines += [
            "",
            f"Covenants: {len(saga.covenants)}",
            f"Characters: {len(saga.characters)}",
            f"Laboratories: {len(saga.laboratories)}",
            f"Books: {len(saga.books)}",
            f"Spells: {len(saga.spells)}",
        ]
        await self._set_detail(Static("\n".join(lines)))

    async def _show_covenant_detail(self, covenant: Covenant) -> None:
        view = CovenantSheetView(self.saga, covenant)
        await self._set_detail(view)
        self._covenant_sheet_view = view
        self._focus_first_section(initial=True)

    async def _show_laboratory_detail(self, lab: Laboratory) -> None:
        view = LaboratorySheetView(self.saga, lab)
        await self._set_detail(view)
        self._laboratory_sheet_view = view
        self._focus_first_section(initial=True)

    async def _show_character_detail(self, character: Character) -> None:
        view = CharacterSheetView(self.saga, character)
        await self._set_detail(view)
        self._character_sheet_view = view
        self._focus_first_section(initial=True)

    async def _show_familiar_detail(self, familiar: Familiar) -> None:
        view = FamiliarSheetView(self.saga, familiar)
        await self._set_detail(view)
        self._familiar_sheet_view = view
        self._focus_first_section(initial=True)

    def _current_sheet_view(
        self,
    ) -> (
        CharacterSheetView
        | LaboratorySheetView
        | CovenantSheetView
        | FamiliarSheetView
        | None
    ):
        """The sheet on show for the selected tree node, if it has one."""
        return {
            "character": self._character_sheet_view,
            "laboratory": self._laboratory_sheet_view,
            "covenant": self._covenant_sheet_view,
            "familiar": self._familiar_sheet_view,
        }.get(self.selected_kind)

    # -- scored-trait lists (Personality Traits, Reputations) --

    def _traits(self, spec: _TraitList) -> list[ScoredTrait] | None:
        owner = getattr(self, spec.owner)
        return None if owner is None else getattr(owner, spec.attr)

    def _trait_prompt(
        self, spec: _TraitList, title: str, existing: ScoredTrait | None = None
    ) -> ScoredTraitPromptScreen:
        return ScoredTraitPromptScreen(
            title, spec.example, existing, **spec.prompt_options
        )

    def _add_trait(self, spec: _TraitList) -> None:
        traits = self._traits(spec)
        if traits is None:
            return

        def handle_result(trait: ScoredTrait | None) -> None:
            if trait is not None:
                traits.append(trait)
                self._commit(spec.section)

        self.app.push_screen(
            self._trait_prompt(spec, f"Add a {spec.noun}"), handle_result
        )

    def _edit_trait(self, spec: _TraitList) -> None:
        """Edit the chosen entry; with none chosen, ask which."""
        traits = self._traits(spec)
        if traits is None:
            return
        self._chosen_or_pick(
            getattr(self, spec.selected)(),
            [label for _, label in st.trait_rows(traits, signed=spec.signed)],
            title=f"Edit which {spec.noun}?",
            empty=f"No {spec.noun}s to edit.",
            then=lambda index: self._edit_trait_at(spec, traits, index),
        )

    def _edit_trait_at(
        self, spec: _TraitList, traits: list[ScoredTrait], index: int
    ) -> None:
        def handle_result(trait: ScoredTrait | None) -> None:
            if trait is not None:
                traits[index] = trait
                self._commit(spec.section)

        self.app.push_screen(
            self._trait_prompt(spec, f"Edit a {spec.noun}", traits[index]),
            handle_result,
        )

    def _remove_trait(self, spec: _TraitList) -> None:
        """Delete the chosen entry (asking first, unless `spec` says not to);
        with none chosen, ask which one."""
        traits = self._traits(spec)
        if traits is None:
            return

        def remove(index: int) -> None:
            if spec.confirm_remove:
                self._confirm_delete(traits, index, traits[index].name, spec.section)
            else:
                del traits[index]
                self._commit(spec.section)

        self._chosen_or_pick(
            getattr(self, spec.selected)(),
            [label for _, label in st.trait_rows(traits, signed=spec.signed)],
            title=f"Remove a {spec.noun}",
            empty=f"No {spec.noun}s to remove.",
            then=remove,
        )

    def _chosen_or_pick(
        self,
        selected: int | None,
        labels: Sequence[str],
        *,
        title: str,
        empty: str,
        then: Callable[[int], object],
    ) -> None:
        """Act on a list entry by index: the chosen row's if there is one
        (`selected`), else the one picked from `labels` in a picker titled
        `title` -- or, with no entries at all, just say `empty`."""
        if selected is not None and selected < len(labels):
            then(selected)
            return
        if not labels:
            self.notify(empty)
            return

        def handle_index(index: int | None) -> None:
            if index is not None:
                then(index)

        self.app.push_screen(RemovalPickerScreen(title, list(labels)), handle_index)

    def _confirm_delete(
        self, entries: list[Any], index: int, name: str, section: str
    ) -> None:
        """Ask "Delete <name>?" (No by default); on Yes, delete
        `entries[index]`, save and refresh `section`."""

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                del entries[index]
                self._commit(section)

        self.app.push_screen(ConfirmScreen(f"Delete {escape(name)}?"), handle_confirmed)

    def _commit(self, *sections: str, tree: bool = False) -> None:
        """Save a change: write the saga, rebuild the navigation tree if a
        name or the structure changed (`tree`), and refresh `sections` of the
        sheet on show -- the one whose handler made the change."""
        storage.save_saga(self.saga)
        if tree:
            self._rebuild_tree()
        view = self._current_sheet_view()
        if view is not None:
            for section in sections:
                view.refresh_section(section)

    def _refresh_character_section(self, section_id: str) -> None:
        if self._character_sheet_view is not None:
            self._character_sheet_view.refresh_section(section_id)

    def _refresh_covenant_section(self, section_id: str) -> None:
        if self._covenant_sheet_view is not None:
            self._covenant_sheet_view.refresh_section(section_id)

    def _refresh_familiar_section(self, section_id: str) -> None:
        if self._familiar_sheet_view is not None:
            self._familiar_sheet_view.refresh_section(section_id)

    def _refresh_laboratory_section(self, section_id: str) -> None:
        if self._laboratory_sheet_view is not None:
            self._laboratory_sheet_view.refresh_section(section_id)

    # -- creation actions --

    def action_create_covenant(self) -> None:
        async def handle_result(covenant_id: str | None) -> None:
            if covenant_id is not None:
                self._rebuild_tree()
                covenant = next(c for c in self.saga.covenants if c.id == covenant_id)
                self.selected_covenant = covenant
                self.selected_kind = "covenant"
                await self._show_covenant_detail(covenant)

        self.app.push_screen(CovenantCreateScreen(self.saga), handle_result)

    def action_create_character(self) -> None:
        covenant = self.selected_covenant

        async def handle_result(character_id: str | None) -> None:
            if character_id is not None:
                self._rebuild_tree()
                character = next(
                    c for c in self.saga.characters if c.id == character_id
                )
                self.selected_character = character
                self.selected_kind = "character"
                await self._show_character_detail(character)

        self.app.push_screen(
            CharacterCreateScreen(
                self.saga, default_covenant_id=covenant.id if covenant else None
            ),
            handle_result,
        )

    def action_create_laboratory(self) -> None:
        covenant = self.selected_covenant

        async def handle_result(lab_id: str | None) -> None:
            if lab_id is not None:
                self._rebuild_tree()
                lab = next(lab for lab in self.saga.laboratories if lab.id == lab_id)
                self.selected_laboratory = lab
                self.selected_kind = "laboratory"
                await self._show_laboratory_detail(lab)

        self.app.push_screen(LaboratoryCreateScreen(self.saga, covenant), handle_result)

    def action_create_familiar(self) -> None:
        if not fam.unbonded_magi(self.saga):
            self.notify("Every magus already has a bound Familiar.")
            return
        character = self.selected_character
        default_magus_id = (
            character.id
            if character is not None
            and character.type == "magus"
            and fam.familiar_of(self.saga, character.id) is None
            else None
        )

        async def handle_result(familiar_id: str | None) -> None:
            if familiar_id is not None:
                self._rebuild_tree()
                familiar = next(f for f in self.saga.familiars if f.id == familiar_id)
                self.selected_familiar = familiar
                self.selected_character = self.saga.character(familiar.character_id)
                self.selected_kind = "familiar"
                await self._show_familiar_detail(familiar)

        self.app.push_screen(
            FamiliarCreateScreen(self.saga, default_magus_id), handle_result
        )

    # -- generic Add/Remove/Edit dispatch, by the active section of any sheet --

    @cached_property
    def _section_ops(self) -> dict[str, _SectionOps]:
        """What a/A/e/r do in each sheet section, keyed by the section id
        _active_section() reports. check_action enables a key only where it
        has an entry here, so a binding and its action can't disagree. Built
        once: check_action runs on every Footer refresh."""
        ops: dict[str, _SectionOps] = {
            SPELL_SECTION: _SectionOps(
                lambda: self._spell_form(None),
                self._remove_saga_spell,
                self._edit_saga_spell,
            ),
            # Character sheet
            "section-char-info": _SectionOps(edit=self._edit_character_info),
            "section-char-characteristics": _SectionOps(
                edit=self._edit_characteristics
            ),
            "section-char-biographical": _SectionOps(
                edit=self._edit_biographical_detail
            ),
            "tab-abilities": _SectionOps(
                self._add_ability, self._remove_ability, self._edit_ability
            ),
            "section-aging": _SectionOps(edit=self._edit_aging),
            # Health has two dialogs behind two Edit buttons (Wounds and
            # Fatigue); 'e' opens Wounds, Fatigue is button-only.
            "section-char-health": _SectionOps(edit=self._edit_wounds),
            "section-arts": _SectionOps(edit=self._edit_arts),
            "section-hermetic-background": _SectionOps(
                edit=self._edit_hermetic_background
            ),
            "section-known-spells": _SectionOps(
                self._add_spell, self._remove_spell, self._edit_spell_mastery
            ),
            "section-inventory": _SectionOps(
                self._add_item, self._remove_item, self._edit_item
            ),
            "section-raw-vis-hermetic": _SectionOps(
                self._add_raw_vis, self._remove_raw_vis, self._edit_raw_vis
            ),
            "section-raw-vis-inventory": _SectionOps(
                self._add_raw_vis, self._remove_raw_vis, self._edit_raw_vis
            ),
            # Familiar sheet
            "section-fam-info": _SectionOps(edit=self._edit_familiar_info),
            "section-fam-binding": _SectionOps(edit=self._edit_familiar_binding),
            "section-fam-characteristics": _SectionOps(
                edit=self._edit_familiar_characteristics
            ),
            "section-fam-health": _SectionOps(edit=self._edit_familiar_wounds),
            "section-fam-natural-weapons": _SectionOps(
                self._add_familiar_natural_weapon,
                self._remove_familiar_natural_weapon,
                self._edit_familiar_natural_weapon,
            ),
            "tab-fam-abilities": _SectionOps(
                self._add_familiar_ability,
                self._remove_familiar_ability,
                self._edit_familiar_ability,
            ),
            "tab-fam-powers": _SectionOps(
                self._add_familiar_bond_power,
                self._remove_familiar_bond_power,
                self._edit_familiar_bond_power,
            ),
            # Laboratory sheet
            "section-lab-identity": _SectionOps(edit=self._edit_lab_identity),
            "section-lab-characteristics": _SectionOps(
                edit=self._edit_lab_characteristics
            ),
            "section-lab-specialties": _SectionOps(
                self._add_specialty, self._remove_specialty, self._edit_specialty
            ),
            "section-lab-features": _SectionOps(
                self._add_feature, self._remove_feature, self._edit_feature
            ),
            "section-lab-rooms": _SectionOps(
                self._add_room, self._remove_room, self._edit_room
            ),
            "section-lab-raw-vis": _SectionOps(
                self._add_lab_raw_vis, self._remove_lab_raw_vis, self._edit_lab_raw_vis
            ),
            "section-lab-items": _SectionOps(
                self._add_inventory_item,
                self._remove_inventory_item,
                self._edit_inventory_item,
            ),
            "tab-lab-diary": _SectionOps(
                self._add_diary_entry, self._remove_diary_entry, self._edit_diary_entry
            ),
            # Covenant sheet
            "section-cov-info": _SectionOps(edit=self._edit_covenant),
            "section-cov-description": _SectionOps(
                edit=self._edit_covenant_description
            ),
            "section-cov-boons": _SectionOps(
                lambda: self._add_boon_hook("Boon"),
                lambda: self._remove_boon_hook("Boon"),
                lambda: self._edit_boon_hook("Boon"),
            ),
            "section-cov-hooks": _SectionOps(
                lambda: self._add_boon_hook("Hook"),
                lambda: self._remove_boon_hook("Hook"),
                lambda: self._edit_boon_hook("Hook"),
            ),
            "section-eco-wealth": _SectionOps(edit=self._edit_wealth),
            "section-eco-income": _SectionOps(
                self._add_income_source,
                self._remove_income_source,
                self._edit_income_source,
            ),
            "section-eco-expenditure": _SectionOps(
                edit=lambda: self._edit_economics_row("expenditure")
            ),
            "section-eco-savings": _SectionOps(
                edit=lambda: self._edit_economics_row("savings")
            ),
            "section-inh-loyalty": _SectionOps(edit=self._edit_loyalty),
            "section-inh-population": _SectionOps(edit=self._edit_population),
            "section-inh-misc": _SectionOps(edit=self._edit_miscellaneous),
        }
        for spec in (
            _CHARACTER_TRAITS,
            _CHARACTER_REPUTATIONS,
            _FAMILIAR_TRAITS,
            _FAMILIAR_REPUTATIONS,
            _COVENANT_REPUTATIONS,
        ):
            ops[spec.section] = _SectionOps(
                partial(self._add_trait, spec),
                partial(self._remove_trait, spec),
                partial(self._edit_trait, spec),
            )
        for section in BOOK_SECTIONS:
            listed = section != "section-lib-summary"  # the summary lists none
            ops[section] = _SectionOps(
                lambda: self._book_form(None),
                self._remove_book if listed else None,
                self._edit_book if listed else None,
            )
        for kind in INHABITANT_KINDS:
            ops[f"section-inh-{kind}"] = _SectionOps(
                partial(self._add_inhabitant, kind),
                partial(self._remove_inhabitant, kind),
                partial(self._edit_inhabitant, kind),
                # Only Magi/Companions can go "departed" (Inhabitant.departed).
                partial(self._restore_inhabitant, kind)
                if kind in inh.AUTO_KINDS
                else None,
            )
        for kind in POSSESSION_KINDS:
            ops[f"section-pos-{kind}"] = _SectionOps(
                partial(self._add_possession, kind),
                partial(self._remove_possession, kind),
                partial(self._edit_possession, kind),
            )
        return ops

    def _section_op(self, name: str) -> Callable[[], None] | None:
        """The active section's handler for `name` ("add", "remove", "edit"
        or "restore"), if it has one."""
        ops = self._section_ops.get(self._active_section() or "")
        return None if ops is None else getattr(ops, name)

    def action_add(self) -> None:
        if (handler := self._section_op("add")) is not None:
            handler()

    def action_remove(self) -> None:
        if (handler := self._section_op("remove")) is not None:
            handler()

    def action_edit(self) -> None:
        if self.selected_kind == "saga":
            self._edit_saga()
        elif (handler := self._section_op("edit")) is not None:
            handler()

    def action_restore(self) -> None:
        if (handler := self._section_op("restore")) is not None:
            handler()

    # -- Spells (the saga's Spells view) --

    def _spells_label(self) -> str:
        return f"Spells ({len(spl.all_spells(self.saga))})"

    def _spell_view(self) -> SpellListView | None:
        try:
            return self.query_one("#detail-pane").query(SpellListView).first()
        except NoMatches:
            return None

    def _spells_changed(self) -> None:
        view = self._spell_view()
        if view is not None:
            view.refilter()
        node = _tree_node_with_data(self.query_one("#nav-tree", Tree), ("spells",))
        if node is not None:
            node.set_label(self._spells_label())

    def _chosen_own_spell(self, verb: str) -> Spell | None:
        """The chosen spell if it's one of the saga's own; otherwise say why
        not (nothing chosen, or a read-only catalog spell)."""
        view = self._spell_view()
        spell = view.selected_spell() if view is not None else None
        if spell is None:
            self.notify(f"Choose a spell to {verb} first.")
            return None
        if not spl.is_own(self.saga, spell):
            self.notify(
                f"{escape(spell.name)} is a catalog spell, so it's read-only. To "
                "make your own version, add a spell with a."
            )
            return None
        return spell

    def _edit_saga_spell(self) -> None:
        spell = self._chosen_own_spell("edit")
        if spell is not None:
            self._spell_form(spell)

    def _spell_form(self, spell: Spell | None) -> None:
        saga = self.saga
        title = "Add a Spell" if spell is None else f"Edit {escape(spell.name)}"

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            target = spell
            if target is None:
                target = spl.add_own_spell(
                    saga, values["name"], values["technique"], values["form"]
                )
            _spell_from_values(target, values)
            storage.save_saga(saga)
            self._spells_changed()

        self.app.push_screen(
            FieldsDialog(
                title,
                _spell_fields(spell),
                validate=_spell_problem,
                live=_spell_live,
            ),
            handle_result,
        )

    def _remove_saga_spell(self) -> None:
        spell = self._chosen_own_spell("delete")
        if spell is None:
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed and spell in self.saga.spells:
                self.saga.spells.remove(spell)
                storage.save_saga(self.saga)
                self._spells_changed()

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(spell.name)}?"), handle_confirmed
        )

    # -- Books (Library tab, laboratory/character Books, Unassigned Books) --

    def _book_view(self) -> BookListView | None:
        """The book list showing in the detail pane, if any (a sheet shows at
        most one)."""
        try:
            return self.query_one("#detail-pane").query(BookListView).first()
        except NoMatches:
            return None

    def _default_book_owner(self) -> str:
        """Owner a new book starts with: wherever it's being added from."""
        if self.selected_kind == "character" and self.selected_character:
            return bk.owner_value("character", self.selected_character.id)
        if self.selected_kind == "laboratory" and self.selected_laboratory:
            return bk.owner_value("laboratory", self.selected_laboratory.id)
        if self.selected_kind == "covenant" and self.selected_covenant:
            return bk.owner_value("covenant", self.selected_covenant.id)
        return ""

    def _pick_book(self, title: str, then: Callable[[Book], None]) -> None:
        """Act on the chosen book; with none chosen, ask which one."""
        view = self._book_view()
        if view is None:
            return
        chosen = view.selected_book()
        if chosen is not None:
            then(chosen)
            return
        listed = list(view.books)
        if not listed:
            self.notify("No books here yet.")
            return

        def handle_index(index: int | None) -> None:
            if index is not None:
                then(listed[index])

        self.app.push_screen(
            RemovalPickerScreen(
                title, [escape(b.name) or "(untitled)" for b in listed]
            ),
            handle_index,
        )

    def _marked_books(self) -> list[Book]:
        view = self._book_view()
        return view.checked_books() if view is not None else []

    def _edit_book(self) -> None:
        """Edit the chosen book; with books marked, change their owner."""
        marked = self._marked_books()
        if marked:
            self._change_owner_of(marked)
            return
        self._pick_book("Edit which book?", self._book_form)

    def _change_owner_of(self, books: list[Book]) -> None:
        """Give several books one new owner (the only edit that makes sense
        for many at once), confirming first."""
        saga = self.saga
        count = len(books)
        plural = "s" if count != 1 else ""
        owners = {bk.owner_value(b.owner_kind, b.owner_id) for b in books}
        current = owners.pop() if len(owners) == 1 else None
        if current is not None and bk.is_unassigned(saga, books[0]):
            current = ""

        def handle_owner(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            owner = values["owner"]
            label = next(lbl for lbl, value in bk.owner_options(saga) if value == owner)

            def handle_confirmed(confirmed: bool | None) -> None:
                if not confirmed:
                    return
                kind, owner_id = bk.parse_owner_value(owner)
                for book in books:
                    book.owner_kind, book.owner_id = kind, owner_id
                storage.save_saga(saga)
                self._books_changed()

            self.app.push_screen(
                ConfirmScreen(
                    f"Changing ownership of {count} book{plural} to "
                    f"[b]{escape(label)}[/]. Continue?",
                    yes_label="Change",
                    yes_variant="success",
                ),
                handle_confirmed,
            )

        self.app.push_screen(
            FieldsDialog(
                f"Change the owner of {count} book{plural}",
                [
                    DialogField(
                        "_books",
                        "Books",
                        "info",
                        ", ".join(b.name or "(untitled)" for b in books),
                    ),
                    DialogField(
                        "owner",
                        "New owner",
                        "select",
                        current,
                        options=bk.owner_options(saga),
                        required=True,
                        allow_blank=True,
                        placeholder="(choose the new owner)",
                    ),
                ],
            ),
            handle_owner,
        )

    def _book_form(self, book: Book | None) -> None:
        saga = self.saga
        title = (
            "Add a Book" if book is None else f"Edit {escape(book.name or 'this book')}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            target = book
            if target is None:
                target = bk.add_book(saga, values["name"], values["type"])
            _book_from_values(target, values, saga)
            storage.save_saga(saga)
            self._books_changed()

        self.app.push_screen(
            FieldsDialog(
                title,
                _book_fields(saga, book, self._default_book_owner()),
                validate=bk.form_problem,
                live=lambda values: _book_live(values, saga),
            ),
            handle_result,
        )

    def _remove_book(self) -> None:
        """Delete the chosen book, or every marked one, after confirming."""
        marked = self._marked_books()
        if marked:
            count = len(marked)

            def handle_all(confirmed: bool | None) -> None:
                if not confirmed:
                    return
                for book in marked:
                    if book in self.saga.books:
                        self.saga.books.remove(book)
                storage.save_saga(self.saga)
                self._books_changed()

            self.app.push_screen(
                ConfirmScreen(
                    f"Are you sure you want to delete {count} "
                    f"book{'s' if count != 1 else ''}?"
                ),
                handle_all,
            )
            return

        def confirm(book: Book) -> None:
            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed and book in self.saga.books:
                    self.saga.books.remove(book)
                    storage.save_saga(self.saga)
                    self._books_changed()

            self.app.push_screen(
                ConfirmScreen(f"Delete {escape(book.name or 'this book')}?"),
                handle_confirmed,
            )

        self._pick_book("Remove a Book", confirm)

    def action_import_data(self) -> None:
        """'I': on the saga, choose what to import (Books or Spells so far);
        on a covenant's Library tab, import books straight into its library."""
        if self.selected_kind == "saga":

            def handle_kind(kind: str | None) -> None:
                if kind == "books":
                    self._import_books(None)
                elif kind == "spells":
                    self._import_spells()

            self.app.push_screen(ImportScreen(), handle_kind)
        elif (
            self.selected_covenant is not None
            and self._active_section() in _LIBRARY_SECTIONS
        ):
            self._import_books(self.selected_covenant)

    def _import_books(self, covenant: Covenant | None) -> None:
        """Pick a CSV file, preview what it holds, then add its books: all
        owned by `covenant`, or all unassigned when it's None (the file's own
        owner column isn't used)."""
        saga = self.saga
        destination = (
            f"into {covenant.name}'s library"
            if covenant is not None
            else "as unassigned books"
        )

        def handle_path(path: Path | None) -> None:
            if path is None:
                return
            try:
                result = bk.read_books_csv(path)
            except (OSError, ValueError) as problem:
                self.notify(
                    f"Couldn't read {escape(path.name)}: {escape(str(problem))}",
                    severity="error",
                )
                return
            if not result.books:
                reason = f" {escape(result.skipped[0])}" if result.skipped else ""
                self.notify(
                    f"No books to import from {escape(path.name)}.{reason}",
                    severity="warning",
                )
                return

            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed:
                    self._add_imported_books(result.books, covenant, destination)

            self.app.push_screen(
                ConfirmScreen(
                    bk.import_preview(
                        result, path.name, destination, {b.name for b in saga.books}
                    ),
                    yes_label="Import",
                    yes_variant="success",
                ),
                handle_confirmed,
            )

        title = (
            f"Import books into {covenant.name}'s library"
            if covenant is not None
            else "Import books (as unassigned books)"
        )
        self.app.push_screen(CsvFilePickerScreen(title, Path.cwd()), handle_path)

    def _add_imported_books(
        self, books: list[Book], covenant: Covenant | None, destination: str
    ) -> None:
        """Add confirmed imported books, asking about each one whose name is
        already taken (Duplicate / Duplicate All / Skip / Skip All). Nothing
        is added until every question is answered."""
        saga = self.saga

        def finish(accepted: list[Book], skipped: int) -> None:
            bk.add_imported_books(saga, accepted, covenant)
            if accepted:
                storage.save_saga(saga)
                self._books_changed()
                if self.selected_kind == "saga":
                    self.call_later(self._show_saga_detail)  # its Books count
            count = len(accepted)
            message = f"Imported {count} book{'s' if count != 1 else ''}"
            message += f" {destination}" if count else ""
            if skipped:
                message += f"; skipped {skipped} duplicate{'s' if skipped != 1 else ''}"
            self.notify(escape(message + "."))

        self._ask_about_duplicates(books, {b.name for b in saga.books}, "book", finish)

    def _ask_about_duplicates(
        self,
        items: list[Any],
        names: set[str],
        noun: str,
        finish: Callable[[list[Any], int], None],
    ) -> None:
        """Go through imported items (anything with a `.name`), asking about
        each whose name is already taken -- by `names` or earlier in `items` --
        (Duplicate / Duplicate All / Skip / Skip All), then call
        `finish(accepted, skipped)`. Nothing is added until every question is
        answered."""
        pending = list(items)
        accepted: list[Any] = []
        taken = set(names)
        state: dict[str, Any] = {"all": None, "skipped": 0}

        def take(item: Any, answer: str) -> None:
            if answer == "skip":
                state["skipped"] += 1
            else:
                accepted.append(item)
                taken.add(item.name)

        def step() -> None:
            while pending:
                item = pending[0]
                if item.name in taken and state["all"] is None:
                    remaining = len(bk.duplicate_names(pending[1:], taken))

                    def handle_answer(answer: str | None, item=item) -> None:
                        answer = answer or "skip"
                        if answer.endswith("_all"):
                            answer = answer[: -len("_all")]
                            state["all"] = answer
                        pending.pop(0)
                        take(item, answer)
                        step()

                    self.app.push_screen(
                        DuplicateBookScreen(item.name, remaining, noun=noun),
                        handle_answer,
                    )
                    return
                pending.pop(0)
                take(item, state["all"] if item.name in taken else "duplicate")
            finish(accepted, state["skipped"])

        step()

    def _import_spells(self) -> None:
        """The Import Spells helper, then pick a CSV, preview it, and add its
        spells to the saga's own (asking about duplicate names)."""
        saga = self.saga

        def handle_path(path: Path | None) -> None:
            if path is None:
                return
            try:
                result = spl.read_spells_csv(path)
            except (OSError, ValueError) as problem:
                self.notify(
                    f"Couldn't read {escape(path.name)}: {escape(str(problem))}",
                    severity="error",
                )
                return
            if not result.spells:
                reason = f" {escape(result.skipped[0])}" if result.skipped else ""
                self.notify(
                    f"No spells to import from {escape(path.name)}.{reason}",
                    severity="warning",
                )
                return
            existing = {sp.name for sp in spl.all_spells(saga)}

            def finish(accepted: list[Spell], skipped: int) -> None:
                spl.add_imported_spells(saga, accepted)
                if accepted:
                    storage.save_saga(saga)
                    self._spells_changed()
                count = len(accepted)
                message = f"Imported {count} spell{'s' if count != 1 else ''}"
                if skipped:
                    message += (
                        f"; skipped {skipped} duplicate{'s' if skipped != 1 else ''}"
                    )
                self.notify(escape(message + "."))

            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed:
                    self._ask_about_duplicates(result.spells, existing, "spell", finish)

            self.app.push_screen(
                ConfirmScreen(
                    spl.spell_import_preview(result, path.name, existing),
                    yes_label="Import",
                    yes_variant="success",
                ),
                handle_confirmed,
            )

        def handle_helper(choice: str | None) -> None:
            if choice == "choose":
                self.app.push_screen(
                    CsvFilePickerScreen(
                        "Import spells (into the saga's own spells)", Path.cwd()
                    ),
                    handle_path,
                )

        self.app.push_screen(SpellImportHelperScreen(Path.cwd()), handle_helper)

    def _books_changed(self) -> None:
        """After any book edit: re-render the book list on show, and keep the
        tree's Unassigned Books node in step (it appears, changes count or goes
        away as books lose and gain owners)."""
        view = self._book_view()
        if view is not None:
            view.rebuild()
        tree = self.query_one("#nav-tree", Tree)
        node = _tree_node_with_data(tree, ("book_group",))
        count = len(bk.unassigned_books(self.saga))
        if node is not None and count:
            node.set_label(f"Unassigned Books ({count})")
        elif node is not None:
            node.remove()
        elif count:
            tree.root.add_leaf(f"Unassigned Books ({count})", data=("book_group",))

    # -- Covenant: Possessions tab --

    def _selected_possession(self, kind: str) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_possession(kind) if view is not None else None

    def _possession_entries(self, kind: str) -> list[pos.PossessionEntry]:
        covenant = self.selected_covenant
        if covenant is None:
            return []
        return pos.entries_for_kind(
            self.saga, covenant, kind, catalog.load_lab_virtue_flaw_catalog_by_id()
        )

    def _add_possession(self, kind: str) -> None:
        self._possession_form(kind, None)

    def _edit_possession(self, kind: str) -> None:
        """Edit the chosen possession; with none chosen, ask which one."""
        entries = self._possession_entries(kind)
        self._chosen_or_pick(
            self._selected_possession(kind),
            [escape(e.name) or "(unnamed)" for e in entries],
            title=f"Edit which {pos.KIND_SINGULAR[kind]}?",
            empty=f"No {pos.KIND_TITLES[kind]} to edit.",
            then=lambda index: self._possession_form(kind, entries[index]),
        )

    def _possession_form(self, kind: str, entry: pos.PossessionEntry | None) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        title = (
            f"Add a {pos.KIND_SINGULAR[kind]}"
            if entry is None
            else f"Edit {escape(entry.name or 'this ' + pos.KIND_SINGULAR[kind].lower())}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            pos.save_entry(covenant, kind, entry, values)
            self._commit(f"section-pos-{kind}")

        self.app.push_screen(
            FieldsDialog(
                title, _possession_fields(kind, entry), validate=pos.form_problem
            ),
            handle_result,
        )

    def _remove_possession(self, kind: str) -> None:
        """Delete the chosen possession (after confirming); with none chosen,
        ask which one. A laboratory listed as a sanctum can't be deleted here."""
        entries = self._possession_entries(kind)
        self._chosen_or_pick(
            self._selected_possession(kind),
            [escape(e.name) or "(unnamed)" for e in entries],
            title=f"Remove a {pos.KIND_SINGULAR[kind]}",
            empty=f"No {pos.KIND_TITLES[kind]} to remove.",
            then=lambda index: self._confirm_remove_possession(kind, entries[index]),
        )

    def _confirm_remove_possession(self, kind: str, entry: pos.PossessionEntry) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        if entry.auto:
            self.notify(
                f"{escape(entry.name)} is a laboratory of this covenant, so it "
                "can't be deleted here. Move it to another covenant from the "
                "laboratory's Identity instead."
            )
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed and entry.record in covenant.possessions:
                covenant.possessions.remove(entry.record)
                self._commit(f"section-pos-{kind}")

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(entry.name or 'this entry')}?"),
            handle_confirmed,
        )

    # -- Covenant: Economics tab --

    #: What the user types on a table row, by `Economics` attribute.
    _ECONOMICS_TYPED_LABELS: ClassVar[dict[str, str]] = {
        "tithes": "Amount (pounds a year)",
        "inflation": "Amount (pounds a year)",
        "sundry": "Amount (pounds a year, at least 1)",
        "magic_savings": "Savings (pounds a year)",
        "emergency_savings": "Savings (pounds a year)",
    }

    def _selected_economics(self, which: str) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_economics(which) if view is not None else None

    def _edit_wealth(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        economics = covenant.economics

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            economics.wealth = values["wealth"]
            self._commit("section-eco-wealth")

        self.app.push_screen(
            FieldsDialog(
                "Edit Wealth",
                [
                    DialogField(
                        "wealth", "Wealth (pounds in stores)", "int", economics.wealth
                    )
                ],
            ),
            handle_result,
        )

    def _add_income_source(self) -> None:
        self._income_form(None)

    def _edit_income_source(self) -> None:
        """Edit the chosen source of income; with none chosen, ask which one."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        sources = covenant.economics.income_sources
        self._chosen_or_pick(
            self._selected_economics("income"),
            [escape(s.name) or "(unnamed)" for s in sources],
            title="Edit which source of income?",
            empty="No sources of income to edit.",
            then=lambda index: self._income_form(sources[index]),
        )

    def _income_form(self, source: IncomeSource | None) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        title = (
            "Add a Source of Income"
            if source is None
            else f"Edit {escape(source.name or 'this source of income')}"
        )
        usual = ", ".join(f"{t} {n}" for t, n in INCOME_TYPE_DEFAULTS.items())
        fields = [
            DialogField(
                "name", "Name", "text", source.name if source else "", required=True
            ),
            DialogField(
                "type",
                "Type",
                "select",
                source.type if source else "Typical",
                options=[(t, t) for t in INCOME_TYPES],
                required=True,
            ),
            DialogField(
                "income",
                "Current Income (blank = usual)",
                "optint",
                source.income if source else None,
                hint=f"Usual per year: {usual}.",
            ),
            DialogField(
                "description",
                "Description",
                "area",
                source.description if source else "",
                hint="Supports **bold** and *italic*.",
            ),
        ]

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            if source is None:
                eco.add_income_source(covenant, values)
            else:
                for key, value in values.items():
                    setattr(source, key, value)
            self._commit("section-eco-income")

        self.app.push_screen(FieldsDialog(title, fields), handle_result)

    def _remove_income_source(self) -> None:
        """Delete the chosen source of income (after confirming); with none
        chosen, ask which one."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        sources = covenant.economics.income_sources
        self._chosen_or_pick(
            self._selected_economics("income"),
            [escape(s.name) or "(unnamed)" for s in sources],
            title="Remove a source of income",
            empty="No sources of income to remove.",
            then=lambda index: self._confirm_remove_income_source(sources[index]),
        )

    def _confirm_remove_income_source(self, source: IncomeSource) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed and source in covenant.economics.income_sources:
                covenant.economics.income_sources.remove(source)
                self._commit("section-eco-income")

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(source.name or 'this source of income')}?"),
            handle_confirmed,
        )

    def _improve_income_source(self) -> None:
        """Improve the chosen source of income (manually simulating a year's
        Income Modification); with none chosen, ask which one."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        sources = covenant.economics.income_sources
        self._chosen_or_pick(
            self._selected_economics("income"),
            [escape(s.name) or "(unnamed)" for s in sources],
            title="Improve which source of income?",
            empty="No sources of income to improve.",
            then=lambda index: self._improve_form(sources[index]),
        )

    def _improve_form(self, source: IncomeSource) -> None:
        def handle_result(result: tuple[int, str] | None) -> None:
            if result is None:
                return
            new_income, note = result
            source.income = new_income
            source.note = note
            self._commit("section-eco-income")

        self.app.push_screen(
            ImproveIncomeScreen(source, self.saga.current_year), handle_result
        )

    def _offer_emergency_draw(
        self, which: str, row: eco.Row, summary: eco.Summary
    ) -> None:
        """With a deficit, editing Emergency Savings first offers to cover it
        from Wealth: all of it, or as much as Wealth holds. No (or no Wealth to
        draw from) goes on to the ordinary form."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        deficit = -summary.surplus_deficit
        draw = eco.emergency_draw(summary)
        if draw == 0:
            self.notify(
                "There's no Wealth to draw from: the covenant is broke.",
                severity="warning",
            )
            self._economics_row_form(which, row, offer_draw=False)
            return
        outcome = (
            f"This moves {draw} from Wealth into Emergency Savings."
            if draw == deficit
            else f"Wealth only covers {draw} of it: all of it is drawn, and "
            f"{deficit - draw} stays uncovered."
        )

        def handle_confirmed(confirmed: bool | None) -> None:
            if not confirmed:
                self._economics_row_form(which, row, offer_draw=False)
                return
            eco.draw_from_wealth(covenant, draw)
            self._commit("section-eco-savings")
            self.notify(f"Drew {draw} from Wealth to cover the deficit.")

        self.app.push_screen(
            ConfirmScreen(
                "Do you wish to draw from Wealth to cover the deficit?\n\n"
                f"Deficit: {deficit}    Wealth: {summary.wealth}\n{outcome}",
                yes_label="Draw",
                yes_variant="success",
            ),
            handle_confirmed,
        )

    def _edit_economics_row(self, which: str) -> None:
        """Edit the chosen Yearly Expenditure / Cost Savings row (its Notes, and
        the numbers that are typed rather than calculated); with none chosen,
        ask which one."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        summary = eco.summarize(self.saga, covenant)
        rows = summary.expenditure if which == "expenditure" else summary.savings
        selected = self._selected_economics(which)
        if selected is not None and selected < len(rows):
            self._economics_row_form(which, rows[selected])
            return

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._economics_row_form(which, rows[index])

        self.app.push_screen(
            RemovalPickerScreen("Edit which row?", [row.name for row in rows]),
            handle_index,
        )

    def _economics_row_form(
        self, which: str, row: eco.Row, *, offer_draw: bool = True
    ) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        if offer_draw and row.key == "emergency_savings":
            summary = eco.summarize(self.saga, covenant)
            if summary.surplus_deficit < 0:
                self._offer_emergency_draw(which, row, summary)
                return
        economics = covenant.economics
        first = "Cost" if which == "expenditure" else "Quantity"
        fields = [DialogField("_n", "Row", "info", row.name)]
        if row.typed:
            fields += [
                DialogField(
                    attribute,
                    self._ECONOMICS_TYPED_LABELS[attribute],
                    "int",
                    getattr(economics, attribute),
                )
                for attribute in row.typed
            ]
        else:
            fields += [
                DialogField(
                    "_c", f"{first} (calculated)", "info", eco.money(row.first)
                ),
                DialogField(
                    "_s", "Savings (calculated)", "info", eco.money(row.savings)
                ),
            ]
        fields.append(
            DialogField("notes", "Notes", "text", economics.notes.get(row.key, ""))
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            eco.apply_row_edit(economics, row.key, values)
            self._commit(f"section-eco-{which}")

        self.app.push_screen(
            FieldsDialog(
                f"Edit {row.name}",
                fields,
                validate=lambda values: eco.row_problem(row.key, values),
            ),
            handle_result,
        )

    # -- Covenant: Inhabitants tab --

    def _selected_inhabitant(self, kind: str) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_inhabitant(kind) if view is not None else None

    def _inhabitant_entries(self, kind: str) -> list[inh.InhabitantEntry]:
        covenant = self.selected_covenant
        if covenant is None:
            return []
        return inh.entries_for_kind(self.saga, covenant, kind)

    def _add_inhabitant(self, kind: str) -> None:
        """Add one. Grog-derived kinds first offer the covenant's unassigned
        grogs (or a brand-new person); Magi, Companions and animals go
        straight to the form."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        if kind not in inh.GROG_KINDS:
            self._inhabitant_form(kind, None, None)
            return

        grogs = inh.available_grogs(self.saga, covenant)
        labels = ["(New person -- not from a character sheet)"] + [
            escape(g.name)
            + (f"  (born {g.background.year_born})" if g.background.year_born else "")
            for g in grogs
        ]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._inhabitant_form(kind, None, grogs[index - 1] if index else None)

        self.app.push_screen(
            RemovalPickerScreen(f"Add a {inh.KIND_SINGULAR[kind]}", labels),
            handle_index,
        )

    def _edit_inhabitant(self, kind: str) -> None:
        """Edit the chosen inhabitant; with none chosen, ask which one."""
        entries = self._inhabitant_entries(kind)
        self._chosen_or_pick(
            self._selected_inhabitant(kind),
            [escape(e.name) or "(unnamed)" for e in entries],
            title=f"Edit which {inh.KIND_SINGULAR[kind]}?",
            empty=f"No {inh.KIND_TITLES[kind]} to edit.",
            then=lambda index: self._inhabitant_form(kind, entries[index], None),
        )

    def _inhabitant_form(
        self, kind: str, entry: inh.InhabitantEntry | None, grog: Character | None
    ) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        title = (
            f"Add a {inh.KIND_SINGULAR[kind]}"
            if entry is None
            else f"Edit {escape(entry.name or 'this ' + inh.KIND_SINGULAR[kind].lower())}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            inh.save_entry(covenant, kind, entry, values, grog)
            self._commit(f"section-inh-{kind}")

        self.app.push_screen(
            FieldsDialog(
                title,
                _inhabitant_fields(kind, entry, grog),
                validate=inh.form_problem,
            ),
            handle_result,
        )

    def _remove_inhabitant(self, kind: str) -> None:
        """Delete the chosen inhabitant (after confirming); with none chosen,
        ask which one. People listed from a character sheet can't be deleted
        here -- that would mean changing the sheet."""
        entries = self._inhabitant_entries(kind)
        self._chosen_or_pick(
            self._selected_inhabitant(kind),
            [escape(e.name) or "(unnamed)" for e in entries],
            title=f"Remove a {inh.KIND_SINGULAR[kind]}",
            empty=f"No {inh.KIND_TITLES[kind]} to remove.",
            then=lambda index: self._confirm_remove_inhabitant(kind, entries[index]),
        )

    def _confirm_remove_inhabitant(self, kind: str, entry: inh.InhabitantEntry) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        name = escape(entry.name or "this entry")

        if entry.auto and entry.character is not None:
            # Listed from a character sheet (e.g. a magus who died): they stay
            # in the covenant on their sheet, but stop counting as an inhabitant.

            def handle_departed(confirmed: bool | None) -> None:
                if not confirmed:
                    return
                inh.mark_departed(covenant, kind, entry)
                self._commit(f"section-inh-{kind}")

            self.app.push_screen(
                ConfirmScreen(
                    f"Remove {name} from the {inh.KIND_TITLES[kind]} list?\n\n"
                    "They stay in the covenant on their character sheet, but "
                    "will no longer count as an inhabitant."
                ),
                handle_departed,
            )
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed and entry.record in covenant.inhabitants:
                covenant.inhabitants.remove(entry.record)
                self._commit(f"section-inh-{kind}")

        self.app.push_screen(ConfirmScreen(f"Delete {name}?"), handle_confirmed)

    def _restore_inhabitant(self, kind: str) -> None:
        """Bring back a departed Magus/Companion: still on their sheet, they
        simply start counting as an inhabitant again."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        entries = inh.departed_entries_for_kind(self.saga, covenant, kind)
        if not entries:
            self.notify(f"No departed {inh.KIND_TITLES[kind]} to restore.")
            return

        def do_restore(entry: inh.InhabitantEntry) -> None:
            if entry.record is not None:
                entry.record.departed = False
                self._commit(f"section-inh-{kind}")

        def handle_index(index: int | None) -> None:
            if index is not None:
                do_restore(entries[index])

        self.app.push_screen(
            RemovalPickerScreen(
                f"Restore which {inh.KIND_SINGULAR[kind]}?",
                [escape(e.name) or "(unnamed)" for e in entries],
            ),
            handle_index,
        )

    def _edit_loyalty(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        loyalty = covenant.loyalty
        styles = inh.governance_names(covenant)
        if styles:
            governance = DialogField(
                "_g",
                "Type of Governance",
                "info",
                f"{', '.join(styles)} (from your Boons)",
            )
        else:
            governance = DialogField(
                "governance", "Type of Governance", "text", loyalty.governance
            )
        base = inh.base_loyalty(self.saga, covenant)
        modifiers = inh.total_modifiers(self.saga, covenant)
        fields = [
            governance,
            DialogField("_bp", "Base Loyalty Points", "info", base),
            DialogField("_tm", "Total modifiers", "info", modifiers),
            DialogField("_cp", "Current Loyalty Points", "info", base + modifiers),
            DialogField(
                "_ps",
                "Prevailing Loyalty Score",
                "info",
                inh.prevailing_loyalty_score(base + modifiers),
            ),
            DialogField(
                "_lc",
                "Living Conditions (from the covenant's Living Conditions (Mundane))",
                "info",
                inh.living_conditions_loyalty(covenant),
            ),
            DialogField(
                "equipment",
                "Equipment",
                "select",
                loyalty.equipment,
                options=[(o, o) for o in LOYALTY_EQUIPMENT],
            ),
            DialogField(
                "money",
                "Money",
                "select",
                loyalty.money,
                options=[(o, o) for o in LOYALTY_MONEY],
            ),
            DialogField(
                "pension",
                "  Pension? (half Wages until death)",
                "check",
                loyalty.pension,
            ),
            DialogField(
                "_sp",
                "Specialists (Presence + Ability of Steward/Chamberlain/Turb "
                "Captain/Autocrat)",
                "info",
                inh.specialists_loyalty(self.saga, covenant),
            ),
            DialogField("familiarity", "Familiarity", "int", loyalty.familiarity),
            DialogField(
                "_rp",
                "Reputation (-5 per point of a known bad Reputation)",
                "info",
                inh.reputation_loyalty_penalty(covenant),
            ),
            DialogField(
                "actions_and_events",
                "Actions and events",
                "int",
                loyalty.actions_and_events,
            ),
            DialogField(
                "magical_influence",
                "Magical Influence",
                "int",
                loyalty.magical_influence,
            ),
        ]

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            for key, value in values.items():
                setattr(loyalty, key, value)
            self._commit("section-inh-loyalty")

        self.app.push_screen(FieldsDialog("Edit Loyalty", fields), handle_result)

    def _edit_population(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        pop = covenant.population
        fields = [
            DialogField(
                "_tm",
                "Number of Teamsters",
                "info",
                inh.other_covenfolk_count(self.saga, covenant, "Teamster"),
            ),
            DialogField(
                "_tn",
                "Teamsters Needed",
                "info",
                inh.minimum_teamsters(self.saga, covenant),
            ),
            DialogField(
                "_sv",
                "Number of Servants",
                "info",
                inh.other_covenfolk_count(self.saga, covenant, "Servant"),
            ),
            DialogField(
                "_sn",
                "Servants Needed",
                "info",
                inh.minimum_servants(self.saga, covenant),
            ),
            DialogField(
                "_lb",
                "Number of Laborers",
                "info",
                inh.other_covenfolk_count(self.saga, covenant, "Laborer"),
            ),
            DialogField("other_people", "Other People", "int", pop.other_people),
            DialogField(
                "_t",
                "Total Inhabitants",
                "info",
                f"{inh.total_inhabitants(self.saga, covenant)} (calculated)",
            ),
        ]

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            for key, value in values.items():
                setattr(pop, key, value)
            self._commit("section-inh-population")

        self.app.push_screen(FieldsDialog("Edit Inhabitants", fields), handle_result)

    def _edit_miscellaneous(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        pop = covenant.population
        fields = [
            DialogField("aging_magi", "Aging for Magi", "int", pop.aging_magi),
            DialogField("aging_mundane", "Aging for Mundane", "int", pop.aging_mundane),
            DialogField("magic_laborers", "Magic Laborers", "int", pop.magic_laborers),
            DialogField("magic_servants", "Magic Servants", "int", pop.magic_servants),
            DialogField(
                "magic_teamsters", "Magic Teamsters", "int", pop.magic_teamsters
            ),
            DialogField("magic_turbula", "Magic Turbula", "int", pop.magic_turbula),
        ]

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            for key, value in values.items():
                setattr(pop, key, value)
            self._commit("section-inh-misc")

        self.app.push_screen(FieldsDialog("Edit Miscellaneous", fields), handle_result)

    # -- Covenant: Description / Reputations / Boons & Hooks --

    def _edit_covenant_description(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return

        def handle_result(text: str | None) -> None:
            if text is not None:
                covenant.notes = text
                self._commit("section-cov-description")

        self.app.push_screen(
            EditCovenantDescriptionScreen(covenant.notes), handle_result
        )

    def _selected_reputation(self) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_reputation() if view is not None else None

    def _attached_boons_hooks(
        self, covenant: Covenant, kind: str
    ) -> list[tuple[int, VirtueFlawInstance]]:
        """The covenant's attached Boons or Hooks (`kind`), each with its
        index into covenant.boons_hooks so callers can edit/delete the real
        entry from a filtered list."""
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        return [
            (index, bh)
            for index, bh in enumerate(covenant.boons_hooks)
            if bh.vf_id in by_id and by_id[bh.vf_id].type == kind
        ]

    def _add_boon_hook(self, kind: str) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        attached_ids = [bh.vf_id for bh in covenant.boons_hooks]

        def handle_result(instance: VirtueFlawInstance | None) -> None:
            if instance is not None:
                covenant.boons_hooks.append(instance)
                self._commit(_BOON_HOOK_SECTION[kind])

        self.app.push_screen(
            CovenantBoonHookPickerScreen(kind, attached_ids), handle_result
        )

    def _selected_boon_hook(self, kind: str) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_boon_hook(kind) if view is not None else None

    def _remove_boon_hook(self, kind: str) -> None:
        """Delete the selected Boon/Hook (after confirming). With nothing
        selected in this section, ask which one first."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        selected = self._selected_boon_hook(kind)
        if selected is not None:
            self._confirm_remove_boon_hook(kind, selected)
            return

        attached = self._attached_boons_hooks(covenant, kind)
        if not attached:
            self.notify(f"No {kind}s to remove.")
            return
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        labels = [catalog.describe_boon_hook(bh, by_id) for _, bh in attached]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._confirm_remove_boon_hook(kind, attached[index][0])

        self.app.push_screen(
            RemovalPickerScreen(f"Remove a {kind}", labels), handle_index
        )

    def _confirm_remove_boon_hook(self, kind: str, index: int) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        label = catalog.describe_boon_hook(covenant.boons_hooks[index], by_id)

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                del covenant.boons_hooks[index]
                self._commit(_BOON_HOOK_SECTION[kind])

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(label)}?"), handle_confirmed
        )

    def _edit_boon_hook(self, kind: str) -> None:
        """Edit the selected Boon/Hook's detail and description. With nothing
        selected in this section, ask which one first."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        selected = self._selected_boon_hook(kind)
        if selected is not None:
            self._edit_boon_hook_at(kind, selected)
            return

        attached = self._attached_boons_hooks(covenant, kind)
        if not attached:
            self.notify(f"No {kind}s to edit.")
            return
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        labels = [catalog.describe_boon_hook(bh, by_id) for _, bh in attached]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._edit_boon_hook_at(kind, attached[index][0])

        self.app.push_screen(
            RemovalPickerScreen(f"Edit which {kind}?", labels), handle_index
        )

    def _edit_boon_hook_at(self, kind: str, index: int) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        instance = covenant.boons_hooks[index]

        def handle_result(result: tuple[str, str] | None) -> None:
            if result is None:
                return
            detail, description = result
            instance.params = boon_hook_params(detail, description, instance.params)
            self._commit(_BOON_HOOK_SECTION[kind])

        self.app.push_screen(
            BoonHookDetailScreen(
                kind,
                by_id[instance.vf_id].name,
                detail=instance.params.get(BOON_HOOK_DETAIL, ""),
                description=instance.params.get(BOON_HOOK_DESCRIPTION, ""),
            ),
            handle_result,
        )

    # -- Covenant --

    def _edit_covenant(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return

        def handle_result(result: dict[str, object] | None) -> None:
            if result is None:
                return
            for field, value in result.items():
                setattr(covenant, field, value)
            self._commit("section-cov-info", tree=True)

        self.app.push_screen(EditCovenantScreen(covenant), handle_result)

    def _edit_saga(self) -> None:
        async def handle_result(result: dict[str, object] | None) -> None:
            if result is None:
                return
            for field, value in result.items():
                setattr(self.saga, field, value)
            self._commit(tree=True)
            self._update_saga_clock()
            await self._show_saga_detail()

        self.app.push_screen(EditSagaScreen(self.saga), handle_result)

    # -- Saga time --

    async def _apply_saga_date(self, season: str, year: int) -> None:
        """Single path for every change to the saga's calendar: store it, then
        refresh everything that inherits it (Header, covenant panel, saga
        summary)."""
        saga = self.saga
        saga.current_season, saga.current_year = season, year
        storage.save_saga(saga)
        self._update_saga_clock()
        self._refresh_covenant_section("section-cov-info")
        if self.selected_kind == "saga":
            await self._show_saga_detail()

    def action_advance_season(self) -> None:
        saga = self.saga

        async def handle_result(confirmed: bool | None) -> None:
            if not confirmed:
                return
            if saga.current_season == SEASONS[-1]:
                in_deficit = eco.covenants_in_deficit(saga)
                if in_deficit:
                    self._offer_to_resolve_deficit(in_deficit, advance)
                    return
            await advance()

        async def advance() -> None:
            new_year = saga.current_season == SEASONS[-1]
            # A new year (Winter -> Spring): each covenant's surplus goes into
            # its Wealth before the date moves on.
            added = eco.close_all_years(saga) if new_year else []
            await self._apply_saga_date(
                *next_season(saga.current_season, saga.current_year)
            )
            message = f"It is now {saga.current_season} {saga.current_year}."
            if added:
                message += " Added to Wealth: " + ", ".join(
                    f"{name} {amount}" for name, amount in added
                )
                message += "."
                self._refresh_covenant_section("section-eco-wealth")
            self.notify(escape(message))

        self.app.push_screen(
            AdvanceSeasonScreen(saga.current_season, saga.current_year),
            handle_result,
        )

    def _offer_to_resolve_deficit(
        self, in_deficit: list[tuple[str, int]], advance: Callable[[], Any]
    ) -> None:
        """Before the year rolls over with a covenant in deficit: Yes (the
        focused, Escape answer) leaves the date alone so the books can be
        balanced; No advances anyway."""
        lines = "\n".join(
            f"  {escape(name)}: {deficit}" for name, deficit in in_deficit
        )

        async def handle_answer(resolve: bool | None) -> None:
            if resolve:
                self.notify(
                    "The year hasn't advanced. Balance the books, then press t again."
                )
                return
            await advance()

        self.app.push_screen(
            ConfirmScreen(
                "The Covenant is currently in a deficit - do you wish to attempt "
                f"to resolve this?\n\n{lines}",
                yes_variant="primary",
                safe_answer=True,
            ),
            handle_answer,
        )

    def action_set_date(self) -> None:
        saga = self.saga

        async def handle_result(result: tuple[str, int] | None) -> None:
            if result is None:
                return
            season, year = result
            if (season, year) == (saga.current_season, saga.current_year):
                return
            await self._apply_saga_date(season, year)
            self.notify(f"Date set to {season} {year}.")

        self.app.push_screen(
            SetDateScreen(saga.current_season, saga.current_year), handle_result
        )

    # -- Character Info / Characteristics --

    def _edit_character_info(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, object] | None) -> None:
            if result is None:
                return
            character.name = cast(str, result["name"])
            character.covenant_id = cast("str | None", result["covenant_id"])
            self.selected_covenant = self.saga.covenant(character.covenant_id)
            if character.type == "magus":
                assign_laboratory(
                    self.saga, character, cast("str | None", result["laboratory_id"])
                )
            character.background.setting = cast(str, result["setting"])
            character.background.confidence_score = cast(
                int, result["confidence_score"]
            )
            character.background.confidence_points = cast(
                int, result["confidence_points"]
            )
            character.background.size = cast(int, result["size"])
            self._commit("section-char-info", tree=True)

        self.app.push_screen(
            EditCharacterInfoScreen(self.saga, character), handle_result
        )

    def _edit_characteristics(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(characteristics: Characteristics | None) -> None:
            if characteristics is not None:
                character.characteristics = characteristics
                self._commit("section-char-characteristics")

        self.app.push_screen(
            EditCharacteristicsScreen(character.characteristics), handle_result
        )

    def _edit_biographical_detail(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, object] | None) -> None:
            if result is not None:
                character.background = cast(Background, result["background"])
                character.description = cast(Description, result["description"])
                self._commit("section-char-biographical")
                # Age (derived from Year Born) lives in the top panel.
                self._refresh_character_section("section-char-info")

        self.app.push_screen(
            EditBiographicalDetailScreen(character.background, character.description),
            handle_result,
        )

    def _edit_aging(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(aging: Aging | None) -> None:
            if aging is not None:
                character.aging = aging
                self._commit("section-aging")

        self.app.push_screen(EditAgingScreen(character.aging), handle_result)

    # -- Abilities --

    def _add_ability(self) -> None:
        character = self.selected_character
        if character is None:
            return
        exclude_names = {a.name for a in character.abilities}

        def handle_result(ability: Ability | None) -> None:
            if ability is not None:
                character.abilities.append(ability)
                self._commit("tab-abilities")

        self.app.push_screen(AbilityPickerScreen(exclude_names), handle_result)

    def _selected_ability(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_ability() if view is not None else None

    @staticmethod
    def _ability_label(a: Ability) -> str:
        specialty = f" ({escape(a.specialty)})" if a.specialty else ""
        return f"{escape(a.name)}{specialty} {a.level} {a.xp}/{a.xp_to_next}"

    def _remove_ability(self) -> None:
        """Delete the chosen Ability (after confirming); with none chosen,
        ask which one first."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_ability(),
            [self._ability_label(a) for a in character.abilities],
            title="Remove an Ability",
            empty="No Abilities to remove.",
            then=lambda index: self._confirm_remove_ability(index),
        )

    def _confirm_remove_ability(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        self._confirm_delete(
            character.abilities, index, character.abilities[index].name, "tab-abilities"
        )

    def _edit_ability(self) -> None:
        """Edit the chosen Ability; with none chosen, ask which one."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_ability(),
            [self._ability_label(a) for a in character.abilities],
            title="Edit which Ability?",
            empty="No Abilities to edit.",
            then=lambda index: self._edit_ability_at(index),
        )

    def _edit_ability_at(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        existing = character.abilities[index]

        def handle_result(ability: Ability | None) -> None:
            if ability is not None:
                character.abilities[index] = ability
                self._commit("tab-abilities")

        self.app.push_screen(
            AbilityDetailsScreen(existing.name, existing.category, existing),
            handle_result,
        )

    # -- Personality Traits / Reputations / Wounds / Fatigue --

    def _selected_personality_trait(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_personality_trait() if view is not None else None

    def _selected_character_reputation(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_reputation() if view is not None else None

    def _edit_wounds(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(wounds: Wounds | None) -> None:
            if wounds is not None:
                character.wounds = wounds
                self._commit("section-char-health")

        self.app.push_screen(EditWoundsScreen(character.wounds), handle_result)

    def _edit_fatigue(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(level: FatigueLevel | None) -> None:
            if level is not None:
                character.fatigue_level = level
                self._commit("section-char-health")

        self.app.push_screen(EditFatigueScreen(character.fatigue_level), handle_result)

    # -- Arts (magi only) --

    def _edit_arts(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(arts: dict[str, ArtScore] | None) -> None:
            if arts is not None:
                character.arts = arts
                self._commit("section-arts")

        self.app.push_screen(EditArtsScreen(character.arts), handle_result)

    # -- Raw Vis / Hermetic Background (magi only) --

    def _add_raw_vis(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: tuple[str, int] | None) -> None:
            if result is not None:
                art, pawns = result
                add_raw_vis(character.raw_vis, art, pawns)
                self._commit("section-raw-vis-hermetic")

        self.app.push_screen(RawVisPromptScreen(), handle_result)

    def _selected_raw_vis(self) -> int | None:
        view = self._character_sheet_view
        section = self._active_section()
        if view is None or section not in (
            "section-raw-vis-hermetic",
            "section-raw-vis-inventory",
        ):
            return None
        return view.selected_raw_vis(section)

    def _edit_raw_vis(self) -> None:
        """Edit the chosen Raw Vis entry; with none chosen, ask which one."""
        character = self.selected_character
        if character is None:
            return
        selected = self._selected_raw_vis()
        if selected is not None:
            self._edit_raw_vis_at(selected)
            return
        if not character.raw_vis:
            self.notify("No Raw Vis to edit.")
            return

        arts = sorted(character.raw_vis)
        labels = [f"{art.title()}: {character.raw_vis[art]} pawn(s)" for art in arts]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._edit_raw_vis_at(index)

        self.app.push_screen(
            RemovalPickerScreen("Edit which Raw Vis entry?", labels), handle_index
        )

    def _edit_raw_vis_at(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        arts = sorted(character.raw_vis)
        old_art = arts[index]

        def handle_result(result: tuple[str, int] | None) -> None:
            if result is not None:
                art, pawns = result
                replace_raw_vis(character.raw_vis, old_art, art, pawns)
                self._commit("section-raw-vis-hermetic")

        self.app.push_screen(
            RawVisPromptScreen(existing=(old_art, character.raw_vis[old_art])),
            handle_result,
        )

    def _remove_raw_vis(self) -> None:
        """Delete the chosen Raw Vis entry (after confirming); with none
        chosen, ask which one first."""
        character = self.selected_character
        if character is None:
            return
        selected = self._selected_raw_vis()
        if selected is not None:
            self._confirm_remove_raw_vis(selected)
            return
        if not character.raw_vis:
            self.notify("No Raw Vis to remove.")
            return

        arts = sorted(character.raw_vis)
        labels = [f"{art.title()}: {character.raw_vis[art]} pawn(s)" for art in arts]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._confirm_remove_raw_vis(index)

        self.app.push_screen(
            RemovalPickerScreen("Remove a Raw Vis entry", labels), handle_index
        )

    def _confirm_remove_raw_vis(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        art = sorted(character.raw_vis)[index]

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                del character.raw_vis[art]
                self._commit("section-raw-vis-hermetic")

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(art.title())}?"), handle_confirmed
        )

    def _edit_hermetic_background(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(hermetic: HermeticBackground | None) -> None:
            if hermetic is not None:
                character.hermetic = hermetic
                self._commit("section-hermetic-background")

        self.app.push_screen(
            EditHermeticBackgroundScreen(character.hermetic), handle_result
        )

    # -- Spells known (magi only) --

    def _add_spell(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(spell_id: str | None) -> None:
            if spell_id is not None:
                character.spells_known.append(KnownSpell(spell_id=spell_id))
                self._commit("section-known-spells")

        self.app.push_screen(
            SpellChooserScreen(
                self.saga,
                exclude={k.spell_id for k in character.spells_known},
                title=f"Add a spell {escape(character.name)} knows",
            ),
            handle_result,
        )

    def _known_spell_labels(self, character: Character) -> list[str]:
        labels = []
        for known in character.spells_known:
            spell = spl.find_spell(self.saga, known.spell_id)
            labels.append(
                escape(spell.name)
                if spell
                else f"{escape(known.spell_id)} (unknown spell)"
            )
        return labels

    def _selected_known_spell(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_known_spell() if view is not None else None

    def _edit_spell_mastery(self) -> None:
        """Edit the chosen known spell's Mastery; with none chosen, ask
        which one."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_known_spell(),
            self._known_spell_labels(character),
            title="Edit Mastery for which spell?",
            empty="No Spells to edit.",
            then=lambda index: self._edit_spell_mastery_at(index),
        )

    def _edit_spell_mastery_at(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        known = character.spells_known[index]
        spell = spl.find_spell(self.saga, known.spell_id)
        name = spell.name if spell else known.spell_id

        def handle_result(result: KnownSpell | None) -> None:
            if result is not None:
                character.spells_known[index] = result
                self._commit("section-known-spells")

        self.app.push_screen(MasteryEditScreen(name, known), handle_result)

    def _remove_spell(self) -> None:
        """Delete the chosen known spell (after confirming); with none
        chosen, ask which one first."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_known_spell(),
            self._known_spell_labels(character),
            title="Remove a Known Spell",
            empty="No Spells to remove.",
            then=lambda index: self._confirm_remove_spell(index),
        )

    def _confirm_remove_spell(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        self._confirm_delete(
            character.spells_known,
            index,
            self._known_spell_labels(character)[index],
            "section-known-spells",
        )

    # -- Inventory --

    def _selected_inventory_item(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_inventory_item() if view is not None else None

    def _add_item(self) -> None:
        """Add an item: ask which kind first (the section is one combined
        list, unlike the covenant Possessions tab's per-kind sections)."""
        character = self.selected_character
        if character is None:
            return

        def handle_kind(index: int | None) -> None:
            if index is not None:
                self._inventory_item_form(("weapon", "armor", "item")[index], None)

        self.app.push_screen(
            RemovalPickerScreen("Add which kind of item?", ["Weapon", "Armor", "Item"]),
            handle_kind,
        )

    def _inventory_item_form(self, kind: str, index: int | None) -> None:
        character = self.selected_character
        if character is None:
            return
        existing = character.inventory[index] if index is not None else None
        entry = pos.PossessionEntry(kind, existing) if existing is not None else None
        title = (
            f"Add a {pos.KIND_SINGULAR[kind]}"
            if index is None
            else f"Edit {escape(existing.name or 'this item')}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            if index is not None and existing is not None:
                for key, value in values.items():
                    setattr(existing, key, value)
            else:
                character.inventory.append(
                    Possession(
                        id=storage.generate_unique_id(
                            values.get("name") or kind,
                            [item.id for item in character.inventory],
                        ),
                        kind=kind,
                        **values,
                    )
                )
            self._commit("section-inventory")

        self.app.push_screen(
            FieldsDialog(
                title, _possession_fields(kind, entry), validate=pos.form_problem
            ),
            handle_result,
        )

    def _edit_item(self) -> None:
        """Edit the chosen item; with none chosen, ask which one."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_inventory_item(),
            [
                pos.row_label(pos.PossessionEntry(item.kind, item))
                for item in character.inventory
            ],
            title="Edit which item?",
            empty="No Items to edit.",
            then=lambda index: self._inventory_item_form(
                character.inventory[index].kind, index
            ),
        )

    def _remove_item(self) -> None:
        """Delete the chosen item (after confirming); with none chosen, ask
        which one first."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_inventory_item(),
            [
                pos.row_label(pos.PossessionEntry(item.kind, item))
                for item in character.inventory
            ],
            title="Remove an Item",
            empty="No Items to remove.",
            then=lambda index: self._confirm_remove_item(index),
        )

    def _confirm_remove_item(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        self._confirm_delete(
            character.inventory,
            index,
            character.inventory[index].name or "this item",
            "section-inventory",
        )

    # -- Laboratory: Identity / Characteristics --

    def _edit_lab_identity(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(result: dict[str, object] | None) -> None:
            if result is None:
                return
            lab.name = cast(str, result["name"])
            lab.location = cast(str, result["location"])
            lab.build_points = cast(int, result["build_points"])
            lab.aura_modifier = cast(int, result["aura_modifier"])
            lab.covenant_id = cast("str | None", result["covenant_id"])
            self.selected_covenant = self.saga.covenant(lab.covenant_id)
            assign_laboratory_owner(
                self.saga, lab, cast("str | None", result["owner_id"])
            )
            self._commit("section-lab-identity", tree=True)

        self.app.push_screen(EditLabIdentityScreen(self.saga, lab), handle_result)

    def _edit_lab_characteristics(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(characteristics: LabCharacteristics | None) -> None:
            if characteristics is not None:
                lab.characteristics = characteristics
                self._commit("section-lab-characteristics")

        self.app.push_screen(
            EditLabCharacteristicsScreen(lab.characteristics), handle_result
        )

    # -- Laboratory: Specialties / Features / Rooms --

    def _add_specialty(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(item: str | None) -> None:
            if item is not None:
                lab.specialties.append(item)
                self._commit("section-lab-specialties")

        self.app.push_screen(ItemAddScreen(), handle_result)

    def _remove_specialty(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.specialties:
            self.notify("No Specialties to remove.")
            return

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.specialties[index]
                self._commit("section-lab-specialties")

        self.app.push_screen(
            RemovalPickerScreen(
                "Remove a Specialty", [escape(s) for s in lab.specialties]
            ),
            handle_result,
        )

    def _add_feature(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(item: str | None) -> None:
            if item is not None:
                lab.features.append(item)
                self._commit("section-lab-features")

        self.app.push_screen(ItemAddScreen(), handle_result)

    def _remove_feature(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.features:
            self.notify("No Features to remove.")
            return

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.features[index]
                self._commit("section-lab-features")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Feature", [escape(f) for f in lab.features]),
            handle_result,
        )

    def _add_room(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(room: NamedDescription | None) -> None:
            if room is not None:
                lab.rooms.append(room)
                self._commit("section-lab-rooms")

        self.app.push_screen(
            NamedDescriptionPromptScreen("Add a Room", "e.g. Vault"), handle_result
        )

    def _remove_room(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.rooms:
            self.notify("No Rooms to remove.")
            return

        labels = [escape(room.name) for room in lab.rooms]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.rooms[index]
                self._commit("section-lab-rooms")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Room", labels), handle_result
        )

    # -- Laboratory: Raw Vis / Items --

    def _add_lab_raw_vis(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(result: tuple[str, int] | None) -> None:
            if result is not None:
                art, pawns = result
                add_raw_vis(lab.raw_vis, art, pawns)
                self._commit("section-lab-raw-vis")

        self.app.push_screen(RawVisPromptScreen(), handle_result)

    def _remove_lab_raw_vis(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.raw_vis:
            self.notify("No Raw Vis to remove.")
            return

        arts = sorted(lab.raw_vis)
        labels = [f"{art.title()}: {lab.raw_vis[art]} pawn(s)" for art in arts]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.raw_vis[arts[index]]
                self._commit("section-lab-raw-vis")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Raw Vis entry", labels), handle_result
        )

    def _add_inventory_item(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(item: NamedDescription | None) -> None:
            if item is not None:
                lab.inventory_items.append(item)
                self._commit("section-lab-items")

        self.app.push_screen(
            NamedDescriptionPromptScreen("Add an Item", "e.g. Silver Mirror"),
            handle_result,
        )

    def _remove_inventory_item(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.inventory_items:
            self.notify("No Items to remove.")
            return

        labels = [escape(item.name) for item in lab.inventory_items]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.inventory_items[index]
                self._commit("section-lab-items")

        self.app.push_screen(
            RemovalPickerScreen("Remove an Item", labels), handle_result
        )

    # -- Laboratory: Diary --

    def _add_diary_entry(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(entry: DiaryEntry | None) -> None:
            if entry is not None:
                lab.diary.append(entry)
                self._commit("tab-lab-diary")

        self.app.push_screen(
            DiaryEntryPromptScreen(
                self.saga.current_year, default_season=self.saga.current_season
            ),
            handle_result,
        )

    def _remove_diary_entry(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.diary:
            self.notify("No Diary entries to remove.")
            return

        labels = [
            f"{entry.year} {entry.season} -- {escape(entry.name)}"
            for entry in lab.diary
        ]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.diary[index]
                self._commit("tab-lab-diary")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Diary Entry", labels), handle_result
        )

    # -- Laboratory: edit an existing list entry --

    def _edit_lab_entry(
        self,
        *,
        picker_title: str,
        empty_message: str,
        labels: list[str],
        screen_for: Callable[[int], ModalScreen[Any]],
        apply: Callable[[int, Any], None],
        section_id: str,
    ) -> None:
        """Shared two-step flow for editing one entry of a laboratory list:
        pick which entry (same picker as Remove), then edit it in a
        pre-filled dialog built by `screen_for(index)`; `apply(index,
        result)` writes the result back before saving and refreshing."""
        if not labels:
            self.notify(empty_message)
            return

        def handle_index(index: int | None) -> None:
            if index is None:
                return

            def handle_result(result: Any) -> None:
                if result is None:
                    return
                apply(index, result)
                self._commit(section_id)

            self.app.push_screen(screen_for(index), handle_result)

        self.app.push_screen(RemovalPickerScreen(picker_title, labels), handle_index)

    def _edit_specialty(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Specialty?",
            empty_message="No Specialties to edit.",
            labels=[escape(s) for s in lab.specialties],
            screen_for=lambda i: ItemAddScreen(
                "Edit a Specialty", existing=lab.specialties[i]
            ),
            apply=lab.specialties.__setitem__,
            section_id="section-lab-specialties",
        )

    def _edit_feature(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Feature?",
            empty_message="No Features to edit.",
            labels=[escape(f) for f in lab.features],
            screen_for=lambda i: ItemAddScreen(
                "Edit a Feature", existing=lab.features[i]
            ),
            apply=lab.features.__setitem__,
            section_id="section-lab-features",
        )

    def _edit_room(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Room?",
            empty_message="No Rooms to edit.",
            labels=[escape(room.name) for room in lab.rooms],
            screen_for=lambda i: NamedDescriptionPromptScreen(
                "Edit a Room", "e.g. Vault", existing=lab.rooms[i]
            ),
            apply=lab.rooms.__setitem__,
            section_id="section-lab-rooms",
        )

    def _edit_inventory_item(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Item?",
            empty_message="No Items to edit.",
            labels=[escape(item.name) for item in lab.inventory_items],
            screen_for=lambda i: NamedDescriptionPromptScreen(
                "Edit an Item", "e.g. Silver Mirror", existing=lab.inventory_items[i]
            ),
            apply=lab.inventory_items.__setitem__,
            section_id="section-lab-items",
        )

    def _edit_lab_raw_vis(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        arts = sorted(lab.raw_vis)

        def apply(index: int, result: tuple[str, int]) -> None:
            art, pawns = result
            replace_raw_vis(lab.raw_vis, arts[index], art, pawns)

        self._edit_lab_entry(
            picker_title="Edit which Raw Vis entry?",
            empty_message="No Raw Vis to edit.",
            labels=[f"{art.title()}: {lab.raw_vis[art]} pawn(s)" for art in arts],
            screen_for=lambda i: RawVisPromptScreen(
                existing=(arts[i], lab.raw_vis[arts[i]])
            ),
            apply=apply,
            section_id="section-lab-raw-vis",
        )

    def _edit_diary_entry(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Diary Entry?",
            empty_message="No Diary entries to edit.",
            labels=[f"{e.year} {e.season} -- {e.name}" for e in lab.diary],
            screen_for=lambda i: DiaryEntryPromptScreen(
                self.saga.current_year, existing=lab.diary[i]
            ),
            apply=lab.diary.__setitem__,
            section_id="tab-lab-diary",
        )

    def action_improve(self) -> None:
        self._improve_income_source()

    # -- shared Character/Laboratory/Familiar Virtue & Flaw actions --

    def action_add_virtue_flaw(self) -> None:
        target = self._virtue_flaw_target()
        if target is None:
            return
        existing_ids = {vf.vf_id for vf in target.virtues_flaws}
        is_lab = self.selected_kind == "laboratory"
        is_familiar = self.selected_kind == "familiar"
        picker = LabVirtueFlawPickerScreen if is_lab else VirtueFlawPickerScreen

        def handle_result(instance: VirtueFlawInstance | None) -> None:
            if instance is not None:
                target.virtues_flaws.append(instance)
                storage.save_saga(self.saga)
                if is_lab:
                    self._refresh_laboratory_section("tab-lab-vf")
                elif is_familiar:
                    self._refresh_familiar_section("section-fam-vf-virtues")
                else:
                    self._refresh_character_section("section-vf-virtues")

        self.app.push_screen(picker(existing_ids), handle_result)

    def action_remove_virtue_flaw(self) -> None:
        is_lab = self.selected_kind == "laboratory"
        is_familiar = self.selected_kind == "familiar"
        if (
            not is_lab
            and not is_familiar
            and self._active_section()
            in (
                "section-vf-virtues",
                "section-vf-flaws",
            )
        ):
            self._remove_character_virtue_flaw()
            return

        target = self._virtue_flaw_target()
        if target is None:
            return
        if not target.virtues_flaws:
            self.notify("No Virtues/Flaws to remove.")
            return

        vf_catalog = (
            catalog.load_lab_virtue_flaw_catalog_by_id()
            if is_lab
            else catalog.load_virtue_flaw_catalog_by_id()
        )
        labels = [
            escape(catalog.describe_virtue_flaw(vf, vf_catalog))
            for vf in target.virtues_flaws
        ]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del target.virtues_flaws[index]
                storage.save_saga(self.saga)
                if is_lab:
                    self._refresh_laboratory_section("tab-lab-vf")
                elif is_familiar:
                    self._refresh_familiar_section("section-fam-vf-virtues")
                else:
                    self._refresh_character_section("section-vf-virtues")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Virtue or Flaw", labels), handle_result
        )

    def _selected_character_virtue_flaw(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_virtue_flaw() if view is not None else None

    def _remove_character_virtue_flaw(self) -> None:
        """Delete the chosen character Virtue/Flaw (after confirming); with
        none chosen, ask which one first."""
        character = self.selected_character
        if character is None:
            return
        selected = self._selected_character_virtue_flaw()
        if selected is not None:
            self._confirm_remove_character_virtue_flaw(selected)
            return
        if not character.virtues_flaws:
            self.notify("No Virtues/Flaws to remove.")
            return

        vf_catalog = catalog.load_virtue_flaw_catalog_by_id()
        labels = [
            escape(catalog.describe_virtue_flaw(vf, vf_catalog))
            for vf in character.virtues_flaws
        ]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._confirm_remove_character_virtue_flaw(index)

        self.app.push_screen(
            RemovalPickerScreen("Remove a Virtue or Flaw", labels), handle_index
        )

    def _confirm_remove_character_virtue_flaw(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        vf_catalog = catalog.load_virtue_flaw_catalog_by_id()
        self._confirm_delete(
            character.virtues_flaws,
            index,
            catalog.describe_virtue_flaw(character.virtues_flaws[index], vf_catalog),
            "section-vf-virtues",
        )

    # -- Familiar: Info & Binding --

    def _edit_familiar_info(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return

        def handle_result(result: dict[str, object] | None) -> None:
            if result is None:
                return
            for field_name, value in result.items():
                setattr(familiar, field_name, value)
            self._commit("section-fam-info", tree=True)

        self.app.push_screen(EditFamiliarInfoScreen(familiar), handle_result)

    def _edit_familiar_binding(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return

        def handle_result(result: dict[str, object] | None) -> None:
            if result is None:
                return
            for field_name, value in result.items():
                setattr(familiar, field_name, value)
            self._commit("section-fam-binding")

        self.app.push_screen(EditFamiliarBindingScreen(familiar), handle_result)

    def _edit_familiar_characteristics(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return

        def handle_result(result: dict[str, object] | None) -> None:
            if result is None:
                return
            familiar.characteristics = result["characteristics"]
            familiar.base_soak = result["base_soak"]
            familiar.magic_resistance = result["magic_resistance"]
            self._commit("section-fam-characteristics")

        self.app.push_screen(EditFamiliarCharacteristicsScreen(familiar), handle_result)

    # -- Familiar: Combat & Health --

    def _edit_familiar_wounds(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return

        def handle_result(wounds: Wounds | None) -> None:
            if wounds is not None:
                familiar.wounds = wounds
                self._commit("section-fam-health")

        self.app.push_screen(EditFamiliarWoundsScreen(familiar.wounds), handle_result)

    def _edit_familiar_fatigue(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return

        def handle_result(level: FatigueLevel | None) -> None:
            if level is not None:
                familiar.fatigue_level = level
                self._commit("section-fam-health")

        self.app.push_screen(EditFatigueScreen(familiar.fatigue_level), handle_result)

    def _selected_familiar_natural_weapon(self) -> int | None:
        view = self._familiar_sheet_view
        return view.selected_natural_weapon() if view is not None else None

    def _familiar_natural_weapon_form(self, index: int | None) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        existing = familiar.natural_weapons[index] if index is not None else None
        entry = (
            pos.PossessionEntry("weapon", existing) if existing is not None else None
        )
        title = (
            "Add a Natural Weapon"
            if index is None
            else f"Edit {escape(existing.name or 'this attack')}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            if index is not None and existing is not None:
                for key, value in values.items():
                    setattr(existing, key, value)
            else:
                familiar.natural_weapons.append(
                    Possession(
                        id=storage.generate_unique_id(
                            values.get("name") or "weapon",
                            [item.id for item in familiar.natural_weapons],
                        ),
                        kind="weapon",
                        **values,
                    )
                )
            self._commit("section-fam-natural-weapons")

        self.app.push_screen(
            FieldsDialog(
                title, _possession_fields("weapon", entry), validate=pos.form_problem
            ),
            handle_result,
        )

    def _add_familiar_natural_weapon(self) -> None:
        self._familiar_natural_weapon_form(None)

    def _edit_familiar_natural_weapon(self) -> None:
        """Edit the chosen attack; with none chosen, ask which one."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_natural_weapon(),
            [
                pos.row_label(pos.PossessionEntry("weapon", weapon))
                for weapon in familiar.natural_weapons
            ],
            title="Edit which attack?",
            empty="No Natural Weapons to edit.",
            then=lambda index: self._familiar_natural_weapon_form(index),
        )

    def _remove_familiar_natural_weapon(self) -> None:
        """Delete the chosen attack (after confirming); with none chosen,
        ask which one first."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_natural_weapon(),
            [
                pos.row_label(pos.PossessionEntry("weapon", weapon))
                for weapon in familiar.natural_weapons
            ],
            title="Remove which attack?",
            empty="No Natural Weapons to remove.",
            then=lambda index: self._confirm_remove_familiar_natural_weapon(index),
        )

    def _confirm_remove_familiar_natural_weapon(self, index: int) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._confirm_delete(
            familiar.natural_weapons,
            index,
            familiar.natural_weapons[index].name or "this attack",
            "section-fam-natural-weapons",
        )

    # -- Familiar: Abilities --

    def _selected_familiar_ability(self) -> int | None:
        view = self._familiar_sheet_view
        return view.selected_ability() if view is not None else None

    def _add_familiar_ability(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        exclude_names = {a.name for a in familiar.abilities}

        def handle_result(ability: Ability | None) -> None:
            if ability is not None:
                familiar.abilities.append(ability)
                self._commit("tab-fam-abilities")

        self.app.push_screen(AbilityPickerScreen(exclude_names), handle_result)

    def _edit_familiar_ability(self) -> None:
        """Edit the chosen Ability; with none chosen, ask which one."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_ability(),
            [self._ability_label(a) for a in familiar.abilities],
            title="Edit which Ability?",
            empty="No Abilities to edit.",
            then=lambda index: self._edit_familiar_ability_at(index),
        )

    def _edit_familiar_ability_at(self, index: int) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        existing = familiar.abilities[index]

        def handle_result(ability: Ability | None) -> None:
            if ability is not None:
                familiar.abilities[index] = ability
                self._commit("tab-fam-abilities")

        self.app.push_screen(
            AbilityDetailsScreen(existing.name, existing.category, existing),
            handle_result,
        )

    def _remove_familiar_ability(self) -> None:
        """Delete the chosen Ability (after confirming); with none chosen,
        ask which one first."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_ability(),
            [self._ability_label(a) for a in familiar.abilities],
            title="Remove an Ability",
            empty="No Abilities to remove.",
            then=lambda index: self._confirm_remove_familiar_ability(index),
        )

    def _confirm_remove_familiar_ability(self, index: int) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._confirm_delete(
            familiar.abilities,
            index,
            familiar.abilities[index].name,
            "tab-fam-abilities",
        )

    # -- Familiar: Bond Powers --

    def _selected_familiar_bond_power(self) -> int | None:
        view = self._familiar_sheet_view
        return view.selected_bond_power() if view is not None else None

    def _familiar_bond_power_form(self, index: int | None) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        existing = familiar.bond_powers[index] if index is not None else None
        title = (
            "Add a Bond Power"
            if existing is None
            else f"Edit {escape(existing.name) or 'this Bond Power'}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            # "select" fields with allow_blank dismiss None for "not set";
            # BondPower uses "" like Familiar.binding_technique/_form do.
            values["technique"] = values.get("technique") or ""
            values["form"] = values.get("form") or ""
            if existing is not None:
                for key, value in values.items():
                    setattr(existing, key, value)
            else:
                familiar.bond_powers.append(
                    BondPower(
                        id=storage.generate_unique_id(
                            values.get("name") or "power",
                            [p.id for p in familiar.bond_powers],
                        ),
                        **values,
                    )
                )
            self._commit("tab-fam-powers")

        self.app.push_screen(
            FieldsDialog(title, _bond_power_fields(existing)), handle_result
        )

    def _add_familiar_bond_power(self) -> None:
        self._familiar_bond_power_form(None)

    def _edit_familiar_bond_power(self) -> None:
        """Edit the chosen Bond Power; with none chosen, ask which one."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_bond_power(),
            [escape(p.name) or "(unnamed)" for p in familiar.bond_powers],
            title="Edit which Bond Power?",
            empty="No Bond Powers to edit.",
            then=lambda index: self._familiar_bond_power_form(index),
        )

    def _remove_familiar_bond_power(self) -> None:
        """Delete the chosen Bond Power (after confirming); with none
        chosen, ask which one first."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_bond_power(),
            [escape(p.name) or "(unnamed)" for p in familiar.bond_powers],
            title="Remove a Bond Power",
            empty="No Bond Powers to remove.",
            then=lambda index: self._confirm_remove_familiar_bond_power(index),
        )

    def _confirm_remove_familiar_bond_power(self, index: int) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._confirm_delete(
            familiar.bond_powers,
            index,
            familiar.bond_powers[index].name or "this Bond Power",
            "tab-fam-powers",
        )

    # -- Familiar: Personality Traits & Reputations --

    def _selected_familiar_personality_trait(self) -> int | None:
        view = self._familiar_sheet_view
        return view.selected_personality_trait() if view is not None else None

    def _selected_familiar_reputation(self) -> int | None:
        view = self._familiar_sheet_view
        return view.selected_reputation() if view is not None else None

    def _virtue_flaw_target(self) -> Character | Laboratory | Familiar | None:
        if (
            self.selected_kind == "laboratory"
            and self._active_section() == "tab-lab-vf"
        ):
            return self.selected_laboratory
        if self.selected_kind == "character" and self._active_section() in (
            "section-vf-virtues",
            "section-vf-flaws",
        ):
            return self.selected_character
        if self.selected_kind == "familiar" and self._active_section() in (
            "section-fam-vf-virtues",
            "section-fam-vf-flaws",
        ):
            return self.selected_familiar
        return None


class SagaPickerScreen(Screen[None]):
    """Lists existing sagas; offers to create a new one or delete one."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("n", "create_saga", "New Saga"),
        ("A", "delete_saga", "Delete Saga"),
        Binding("delete", "delete_saga", "Delete Saga", show=False),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "Select a saga to open, press 'n' to create a new one, "
            "or 'A' to delete the highlighted one.",
            id="picker-hint",
        )
        yield ListView(id="saga-list")
        yield BottomBar()

    async def on_mount(self) -> None:
        await self.refresh_list()

    async def refresh_list(self) -> None:
        list_view = self.query_one("#saga-list", ListView)
        # Must be awaited before re-adding items below, or a same-id item not
        # yet removed collides with its freshly-mounted replacement and
        # Textual raises DuplicateIds.
        await list_view.clear()

        saga_ids = storage.list_sagas()
        if not saga_ids:
            await list_view.append(
                ListItem(Label("No sagas yet -- press 'n' to create one."))
            )
            return

        items = []
        for saga_id in saga_ids:
            saga = storage.load_saga(saga_id)
            summary = (
                f"{escape(saga.name)}  —  "
                f"Storyguide: {escape(saga.storyguide) or '(unset)'}"
                f"  —  {saga.current_season} {saga.current_year}"
            )
            items.append(
                ListItem(Label(summary), id=f"{_SAGA_ITEM_ID_PREFIX}{saga_id}")
            )
        await list_view.extend(items)
        # append()/extend() don't set an initial highlight the way construction-time
        # children do, so keyboard/enter selection wouldn't work without this.
        list_view.index = 0

    def action_create_saga(self) -> None:
        async def handle_result(saga_id: str | None) -> None:
            if saga_id is not None:
                await self.refresh_list()

        self.app.push_screen(SagaCreateScreen(), handle_result)

    def action_delete_saga(self) -> None:
        """Delete the highlighted saga's file, after confirming: this is
        permanent, so the message says so and No is the default."""
        item = self.query_one("#saga-list", ListView).highlighted_child
        if (
            item is None
            or item.id is None
            or not item.id.startswith(_SAGA_ITEM_ID_PREFIX)
        ):
            self.notify("No saga to delete.")
            return
        saga_id = item.id.removeprefix(_SAGA_ITEM_ID_PREFIX)
        try:
            name = storage.load_saga(saga_id).name
        except OSError, ValueError, TypeError, KeyError:
            name = saga_id  # unreadable file: still let it be deleted by id

        async def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                storage.delete_saga(saga_id)
                list_view = self.query_one("#saga-list", ListView)
                index = list_view.index or 0
                await self.refresh_list()
                remaining = len(storage.list_sagas())
                if remaining:  # keep the highlight near where it was
                    list_view.index = min(index, remaining - 1)

        self.app.push_screen(
            ConfirmScreen(
                f"Delete the saga {escape(name)}?\n\n"
                "Everything in it (covenants, characters, laboratories, "
                "library) is deleted for good. This cannot be undone.",
                yes_label="Delete",
            ),
            handle_confirmed,
        )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id is None or not item_id.startswith(_SAGA_ITEM_ID_PREFIX):
            return
        saga_id = item_id.removeprefix(_SAGA_ITEM_ID_PREFIX)
        saga = storage.load_saga(saga_id)
        self.app.push_screen(WorkspaceScreen(saga))
