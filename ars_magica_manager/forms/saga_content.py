"""The Saga Content view's forms, independent of how they are drawn: the
saga's own spells, House Rules, players and sources, which books are in
play, whether a shared catalog is offered, and the single catalog entries
the saga hides. Each section's Add, Edit and Delete are a
commands.SectionOps; the terminal's dialogs build their fields from here
too (except the spell form, whose terminal copy is in
tui/screens/forms/spells.py).

An Edit or Delete the rules refuse (a House Rule a record holds, a
source an entry cites, a catalog spell) is a commands.Refuse saying why.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from .. import house_rules as hr
from .. import own_abilities as oa
from .. import players as pl
from .. import saga_content as sc
from .. import sourcebooks, storyguides, traditions, viewing
from .. import spells as spl
from ..arts import FORMS, TECHNIQUES
from ..commands import Act, Choice, Choose, Confirm, Form, Refuse, SectionOps
from ..form_spec import DialogField, attr, description_field, pairs
from ..markup import escape
from ..models import (
    REALMS,
    SPELL_DURATIONS,
    SPELL_RANGES,
    SPELL_TARGETS,
    SUPERNATURAL_CATEGORIES,
    AbilityDef,
    Player,
    Saga,
    SagaSource,
    Spell,
)
from ..remote import audit
from ..remote.audit import AuditLog, audit_path
from ..remote.devices import DeviceBook, devices_path
from ..remote.passcodes import RemotePasscodes, passcodes_path
from ..rules import spell_levels

# ------------------------------------------------------------------ spells

#: The choice in a Range/Duration/Target select that opens a free-text box.
OTHER = "__other__"


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
            OTHER if other else value,
            options=pairs(standard) + [("Other...", OTHER)],
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
            show_if=lambda v, k=key: v.get(k) == OTHER,
        ),
    ]


def spell_fields(spell: Spell | None, saga: Saga | None = None) -> list[DialogField]:
    """A spell of the saga's own: its Arts, level, Range/Duration/Target,
    ritual, base level (which fills in the level), the saga source it
    cites (source_field) and description."""
    return [
        DialogField("name", "Name", "text", attr(spell, "name", ""), required=True),
        DialogField(
            "technique",
            "Technique",
            "select",
            attr(spell, "technique", ""),
            options=pairs(TECHNIQUES),
            required=True,
            allow_blank=True,
            placeholder="(choose a Technique)",
        ),
        DialogField(
            "form",
            "Form",
            "select",
            attr(spell, "form", ""),
            options=pairs(FORMS),
            required=True,
            allow_blank=True,
            placeholder="(choose a Form)",
        ),
        DialogField(
            "level",
            "Level",
            "optint",
            attr(spell, "level", None),
            hint="Leave blank for a General spell (cast at any level).",
        ),
        DialogField(
            "requisites",
            "Requisites",
            "text",
            ", ".join(attr(spell, "requisites", [])),
            placeholder="e.g. Rego, Corpus",
        ),
        *_rdt_field(
            "range", "Range", SPELL_RANGES, attr(spell, "range", ""), level_fill
        ),
        *_rdt_field(
            "duration",
            "Duration",
            SPELL_DURATIONS,
            attr(spell, "duration", ""),
            level_fill,
        ),
        *_rdt_field(
            "target", "Target", SPELL_TARGETS, attr(spell, "target", ""), level_fill
        ),
        DialogField("ritual", "Ritual", "check", attr(spell, "ritual", False)),
        DialogField(
            "base_level",
            "Base level",
            "optint",
            attr(spell, "base_level", None),
            hint="The guideline's level; with Range, Duration and Target it "
            "fills in Level (add any size or requisite magnitudes yourself).",
            fills=level_fill,
        ),
        *source_field(saga, attr(spell, "source", "")),
        description_field(attr(spell, "description", "")),
    ]


def level_fill(values: dict[str, Any]) -> dict[str, Any]:
    """Level worked out from the base and Range/Duration/Target
    (rules.spell_levels), once they are all standard and given."""
    base = values.get("base_level")
    if base is None:
        return {}
    design = spell_levels.spell_level(
        base,
        spell_rdt(values, "range"),
        spell_rdt(values, "duration"),
        spell_rdt(values, "target"),
        ritual=bool(values.get("ritual")),
    )
    return {} if design is None else {"level": design.level}


def spell_rdt(values: dict[str, Any], key: str) -> str:
    """A Range, Duration or Target as chosen, or as typed under Other."""
    chosen = values.get(key) or ""
    return (values.get(f"{key}_other") or "").strip() if chosen == OTHER else chosen


def spell_from_values(spell: Spell, values: dict[str, Any]) -> None:
    spell.name = values["name"]
    spell.technique = values["technique"]
    spell.form = values["form"]
    spell.level = values.get("level")
    spell.requisites = spl.parse_requisites(values.get("requisites", ""))
    spell.range = spell_rdt(values, "range")
    spell.duration = spell_rdt(values, "duration")
    spell.target = spell_rdt(values, "target")
    spell.ritual = bool(values.get("ritual"))
    spell.base_level = values.get("base_level")
    spell.source = values.get("source") or ""
    spell.description = values.get("description", "")
    spell.details_missing = False


def spell_problem(values: dict[str, Any]) -> str | None:
    if values.get("level") is not None and values["level"] < 1:
        return "Level must be at least 1 (or blank for a General spell)."
    for key, label in (
        ("range", "Range"),
        ("duration", "Duration"),
        ("target", "Target"),
    ):
        if values.get(key) == OTHER and not (values.get(f"{key}_other") or "").strip():
            return f"Type the {label}, or choose one of the standard ones."
    unknown = spl.unknown_requisites(values.get("requisites", ""))
    if unknown:
        return f"Requisites must be Arts (e.g. Rego, Corpus), not {', '.join(unknown)}."
    return None


def spell_live(values: dict[str, Any]) -> str:
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


def read_only_spell(spell: Spell) -> str:
    return (
        f"{escape(spell.name)} is a catalog spell, so it's read-only. To make "
        "your own version, add a spell."
    )


def spell_ops(saga: Saga, listed: Callable[[], Sequence[Spell]]) -> SectionOps:
    """Add, Edit and Delete for the Spells list; `listed` is the spells as
    the list shows them now (filtered), which Edit's and Delete's index
    counts into. Only the saga's own spells change."""

    def form(spell: Spell | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            target = spell
            if target is None:
                target = spl.add_own_spell(
                    saga, values["name"], values["technique"], values["form"]
                )
            spell_from_values(target, values)

        return Form(
            "Add a Spell" if spell is None else f"Edit {escape(spell.name)}",
            lambda: spell_fields(spell, saga),
            apply,
            validate=spell_problem,
            live=spell_live,
        )

    def edit(index: int) -> Form | Refuse:
        spell = listed()[index]
        if not spl.is_own(saga, spell):
            return Refuse("Edit a Spell", read_only_spell(spell))
        return form(spell)

    def remove(index: int) -> Confirm | Refuse:
        spell = listed()[index]
        if not spl.is_own(saga, spell):
            return Refuse("Delete a Spell", read_only_spell(spell))

        def apply() -> None:
            saga.spells[:] = [s for s in saga.spells if s is not spell]

        return Confirm(f"Delete {escape(spell.name)}?", apply)

    return SectionOps(
        add=lambda: form(None),
        edit=edit,
        remove=remove,
        rows=lambda: [spell.name for spell in listed()],
    )


# ------------------------------------------------------------- House Rules

HouseRule = tuple[str, hr.Entry]


def house_rule_title(existing: HouseRule | None) -> str:
    return (
        "Add a House Rule" if existing is None else f"Edit {escape(existing[1].name)}"
    )


def _house_rule_kind(existing: HouseRule | None, values: dict[str, Any]) -> str:
    if existing is not None:
        return existing[0]
    return values.get("kind") or hr.CHARACTER


def house_rule_values(
    existing: HouseRule | None, values: dict[str, Any]
) -> dict[str, Any]:
    """The values house_rules.add / update take (with "kind"), from the
    form's."""
    of = _house_rule_kind(existing, values)
    if of == hr.ABILITY:
        return {
            "kind": of,
            "name": values.get("name") or "",
            "category": values.get(f"category_{of}") or oa.SUPERNATURAL,
            "realm": values.get("realm") or "",
            "characteristic": values.get("characteristic") or "",
            "accelerated": bool(values.get("accelerated")),
            "with_virtue": existing is None and bool(values.get("with_virtue")),
            "virtue_tier": values.get("virtue_tier") or oa.VIRTUE_TIER,
            "description": values.get("description") or "",
            "source": values.get("source") or "",
        }
    covenant = of == hr.COVENANT
    return {
        "kind": of,
        "name": values.get("name") or "",
        "type": values.get("bh_type" if covenant else "vf_type"),
        "tier": values.get("tier"),
        "category": values.get(f"category_{of}"),
        "repeatable": bool(values.get("repeatable")),
        "description": values.get("description") or "",
        "source": values.get("source") or "",
        "parameters": hr.parse_choices(values.get("asks") or ""),
    }


def house_rule_problem(
    saga: Saga, existing: HouseRule | None, values: dict[str, Any]
) -> str | None:
    built = house_rule_values(existing, values)
    return hr.form_problem(
        saga, built["kind"], built, existing[1] if existing is not None else None
    )


def house_rule_live(existing: HouseRule | None, values: dict[str, Any]) -> str:
    built = house_rule_values(existing, values)
    if built["kind"] == hr.ABILITY:
        return ability_live(built)
    return (
        hr.points_text(built["type"], built["tier"])
        + ". Text only: no effects are applied."
    )


def house_rule_fields(saga: Saga, existing: HouseRule | None) -> list[DialogField]:
    """A user-made catalog entry: what it is for (a character, a laboratory
    or a covenant -- fixed once made), its name, type, tier (which gives
    its points), category, the choices it asks for when taken (not a
    laboratory's), source and description. Text only: the rules engine
    applies no effects for it."""
    kind_now, chosen = existing if existing is not None else (None, None)
    ability = chosen if isinstance(chosen, AbilityDef) else None
    entry = None if isinstance(chosen, AbilityDef) else chosen

    def kind(values: dict[str, Any]) -> str:
        return _house_rule_kind(existing, values)

    def category(of: str) -> DialogField:
        current = chosen.category if chosen is not None and kind_now == of else ""
        first = oa.SUPERNATURAL if of == hr.ABILITY else hr.CATEGORIES[of][0]
        return DialogField(
            f"category_{of}",
            "Category",
            "select",
            current if current in hr.CATEGORIES[of] else first,
            options=pairs(hr.CATEGORIES[of]),
            show_if=lambda values: kind(values) == of,
        )

    covenant_entry = kind_now == hr.COVENANT
    return [
        DialogField("_kind", "For", "info", hr.KIND_LABELS[kind_now])
        if kind_now is not None
        else DialogField(
            "kind",
            "For",
            "select",
            hr.CHARACTER,
            options=[(hr.KIND_LABELS[k], k) for k in hr.KINDS],
        ),
        DialogField(
            "name", "Name", "text", chosen.name if chosen else "", required=True
        ),
        DialogField(
            "vf_type",
            "Type",
            "select",
            entry.type if entry is not None and not covenant_entry else "Virtue",
            options=pairs(hr.TYPES[hr.CHARACTER]),
            show_if=lambda values: kind(values) not in (hr.COVENANT, hr.ABILITY),
        ),
        DialogField(
            "bh_type",
            "Type",
            "select",
            entry.type if entry is not None and covenant_entry else "Boon",
            options=pairs(hr.TYPES[hr.COVENANT]),
            show_if=lambda values: kind(values) == hr.COVENANT,
        ),
        DialogField(
            "tier",
            "Tier",
            "select",
            entry.tier if entry else "Minor",
            options=pairs(hr.TIERS),
            show_if=lambda values: kind(values) != hr.ABILITY,
        ),
        *(category(of) for of in hr.KINDS),
        *ability_fields(existing is None, ability, kind),
        DialogField(
            "repeatable",
            "Can be taken more than once",
            "check",
            bool(entry.repeatable) if entry else False,
            show_if=lambda values: kind(values) != hr.ABILITY,
        ),
        DialogField(
            "asks",
            "Asks for",
            "text",
            ", ".join(getattr(entry, "parameters", []) or []).title()
            if entry is not None and kind_now in hr.ASKING_KINDS
            else "",
            placeholder="e.g. Form, or Ability (blank: nothing)",
            hint="What is chosen as it is taken, comma-separated. "
            + ", ".join(c.title() for c in hr.LISTED_CHOICES)
            + " are picked from a list; anything else is typed.",
            show_if=lambda values: kind(values) in hr.ASKING_KINDS,
        ),
        *source_field(saga, chosen.source if chosen is not None else ""),
        description_field(chosen.description if chosen else ""),
    ]


def ability_fields(
    adding: bool, ability: AbilityDef | None, kind: Callable[[dict[str, Any]], str]
) -> list[DialogField]:
    """One of the saga's own Abilities (own_abilities.py): the realm a
    Supernatural one is affiliated with, the Characteristic it rolls with,
    whether it is Accelerated, and (when adding) its Supernatural Virtue,
    Major or Minor (Houses of Hermes: Societates p. 104; DE p. 106)."""

    def shown(values: dict[str, Any]) -> bool:
        return kind(values) == hr.ABILITY

    def special(values: dict[str, Any]) -> bool:
        return shown(values) and (
            values.get(f"category_{hr.ABILITY}") in SUPERNATURAL_CATEGORIES
        )

    realm = ability.realm if ability is not None and ability.realm else ""
    fields = [
        DialogField(
            "realm",
            "Realm",
            "select",
            realm or oa.DEFAULT_REALM,
            options=pairs(REALMS),
            show_if=special,
            hint="Its affiliation: a magus Ex Miscellanea's is usually Magic, "
            "but it may be any realm.",
        ),
        DialogField(
            "characteristic",
            "Rolls with",
            "select",
            (ability.characteristic if ability is not None else "") or None,
            options=pairs(oa.CHARACTERISTICS),
            allow_blank=True,
            placeholder="(the storyguide chooses)",
            show_if=shown,
            hint="Its roll: Characteristic + Ability (+ aura for a "
            "Supernatural one) + die, against an Ease Factor.",
        ),
        DialogField(
            "accelerated",
            "Accelerated",
            "check",
            ability is not None and oa.accelerated(ability),
            show_if=special,
            hint="On the Art table, for Ease Factors like Mights or spell "
            "levels: its spell level is its Casting Total, not 5 x its score.",
        ),
    ]
    if adding:
        fields.append(
            DialogField(
                "with_virtue",
                "Add its Virtue",
                "check",
                True,
                show_if=special,
                hint="Its Supernatural Virtue, of its name, which grants "
                "it (one already offered is not added again).",
            )
        )
        fields.append(
            DialogField(
                "virtue_tier",
                "Its Virtue is",
                "select",
                oa.VIRTUE_TIER,
                options=pairs(oa.VIRTUE_TIERS),
                show_if=lambda values: (
                    special(values) and bool(values.get("with_virtue"))
                ),
                hint="A designed Ability is a Major Virtue's (Societates p. 104); "
                "Minor, as Second Sight is, is the troupe's choice (DE p. 106).",
            )
        )
    return fields


def ability_live(built: dict[str, Any]) -> str:
    """An Ability form's live line: what it rolls, and its Penetration."""
    roll = f"{built['characteristic'] or 'Characteristic'} + {built['name'] or 'it'}"
    if built["category"] not in SUPERNATURAL_CATEGORIES:
        return f"Rolls {escape(roll)} + die."
    return (
        f"Casting Total: {escape(roll)} + aura + die. Penetration: Casting "
        "Total - Ease Factor + Penetration bonus."
    )


def source_field(saga: Saga | None, current: str) -> list[DialogField]:
    """The saga source an entry of the saga's own cites (a House Rule, a
    spell, a good, a Mystery Cult), when the saga has any (Saga Content's
    Saga Sources): out of play with it, like a book. One citing a book
    keeps it among the choices."""
    own = saga.sources if saga is not None else []
    options = [
        (f"{s.title or s.abbreviation} ({s.abbreviation})", s.abbreviation) for s in own
    ]
    if current and current not in {s.abbreviation for s in own}:
        options.insert(0, (f"{sourcebooks.titles(current)} ({current})", current))
    if not options:
        return []
    return [
        DialogField(
            "source",
            "Source",
            "select",
            current or None,
            options=options,
            allow_blank=True,
            placeholder="(none: always in play)",
            hint="Out of play with its source, like an entry from a book.",
        )
    ]


def house_rule_ops(saga: Saga) -> SectionOps:
    """Add, Edit and Delete for the saga's House Rules, in hr.all_entries
    order. An entry a record still holds can't be deleted."""

    def form(existing: HouseRule | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            built = house_rule_values(existing, values)
            if existing is None:
                hr.add(saga, built["kind"], built)
            else:
                hr.update(saga, existing[0], existing[1], built)

        return Form(
            house_rule_title(existing),
            lambda: house_rule_fields(saga, existing),
            apply,
            validate=lambda values: house_rule_problem(saga, existing, values),
            live=lambda values: house_rule_live(existing, values),
        )

    def remove(index: int) -> Confirm | Refuse:
        kind, entry = hr.all_entries(saga)[index]
        holders = hr.used_by(saga, kind, entry)
        if holders:
            return Refuse(
                "Delete a House Rule",
                f"{escape(entry.name)} is held by {escape(', '.join(holders))}: "
                "remove it there first.",
            )
        return Confirm(
            f"Delete {escape(entry.name)}?", lambda: hr.remove(saga, kind, entry)
        )

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(hr.all_entries(saga)[index]),
        remove=remove,
        rows=lambda: [entry.name for _, entry in hr.all_entries(saga)],
    )


#: A Move to Source form's tick for a House Rule is keyed by this and its
#: index in hr.all_entries.
MOVE_KEY = "move-"


def move_to_source(saga: Saga) -> Form | Refuse:
    """Make several House Rules cite one of the saga's sources (or none) at
    once: the source, then a tick for each entry, by its source now."""
    title = "Move to Source"
    entries = hr.all_entries(saga)
    if not saga.sources:
        return Refuse(title, "The saga has no source of its own: add one first.")
    if not entries:
        return Refuse(title, "The saga has no House Rules to move.")

    def fields() -> list[DialogField]:
        return [
            DialogField(
                "source",
                "Move to",
                "select",
                saga.sources[0].abbreviation,
                options=[
                    (f"{s.title or s.abbreviation} ({s.abbreviation})", s.abbreviation)
                    for s in saga.sources
                ],
                allow_blank=True,
                placeholder="(no source: always in play)",
            ),
            *(
                DialogField(
                    f"{MOVE_KEY}{n}",
                    f"{entry.name} ({hr.KIND_SHORT[kind]}, "
                    f"{entry.source or 'no source'})",
                    "check",
                    False,
                )
                for n, (kind, entry) in enumerate(entries)
            ),
        ]

    def validate(values: dict[str, Any]) -> str | None:
        if not any(values.get(f"{MOVE_KEY}{n}") for n in range(len(entries))):
            return "Tick at least one entry to move."
        return None

    def apply(values: dict[str, Any]) -> None:
        source = values.get("source") or ""
        for n, (kind, entry) in enumerate(entries):
            if values.get(f"{MOVE_KEY}{n}"):
                hr.cite(saga, kind, entry, source)

    return Form(title, fields, apply, validate=validate, save_label="Move")


# ----------------------------------------------------------------- players


def player_title(existing: Player | None) -> str:
    return "Add a Player" if existing is None else f"Edit {escape(existing.name)}"


def player_fields(existing: Player | None) -> list[DialogField]:
    """Someone who can sign in to the saga from a browser: their name, role
    and passcode. Editing leaves the passcode blank, which keeps the old
    one."""
    return [
        DialogField(
            "name",
            "Name",
            "text",
            existing.name if existing else "",
            required=True,
            hint="What they type to sign in.",
        ),
        DialogField(
            "role",
            "Role",
            "select",
            existing.role if existing else pl.PLAYER,
            options=[(pl.ROLE_LABELS[r], r) for r in pl.ROLES],
        ),
        DialogField(
            "covenant_rights",
            "May change covenants",
            "check",
            existing.covenant_rights if existing else False,
            show_if=lambda values: values.get("role") == pl.PLAYER,
            hint="A storyguide always may.",
        ),
        DialogField(
            "passcode",
            "Passcode" if existing is None else "New passcode",
            "secret",
            "",
            hint="At least 14 characters: a few words they'll remember, "
            "such as 'grey owl over the mill', are easiest. Give it to them "
            "yourself; it is stored only scrambled. Blank makes a "
            "table-only Player, who can't sign in until given one."
            if existing is None
            else "Blank keeps the one they have.",
        ),
    ]


#: The key of a "Plays <character>" tick, before the character's id.
PLAYS = "plays_character_"


def plays_fields(saga: Saga, existing: Player | None) -> list[DialogField]:
    """A "Plays" tick for each of the troupe's characters (several players
    may tick the same one); for a player, not a storyguide."""

    def a_player(values: dict[str, Any]) -> bool:
        return values.get("role") == pl.PLAYER

    return [
        DialogField(
            f"{PLAYS}{c.id}",
            f"Plays {escape(c.name)}",
            "check",
            existing is not None and existing.id in c.background.player_ids,
            show_if=a_player,
        )
        for c in pl.troupe_characters(saga)
    ]


def apply_plays(saga: Saga, player: Player, values: dict[str, Any]) -> None:
    """Who `player` plays, from the form's Plays ticks."""
    for c in saga.characters:
        key = f"{PLAYS}{c.id}"
        if key not in values:
            continue
        ids = c.background.player_ids
        if values[key] and player.role == pl.PLAYER and player.id not in ids:
            ids.append(player.id)
        elif not (values[key] and player.role == pl.PLAYER) and player.id in ids:
            ids.remove(player.id)


def player_problem(
    saga: Saga, existing: Player | None, values: dict[str, Any]
) -> str | None:
    if values.get("passcode") and (weak := pl.passcode_problem(values["passcode"])):
        return weak
    return pl.name_problem(saga, values.get("name") or "", existing)


def player_form(saga: Saga, existing: Player | None) -> Form:
    """Add (None) or Edit a player: name, role, passcode and whom they play.
    Saga Content's Players and Host for Players both run it."""

    def store(values: dict[str, Any]) -> None:
        was = existing.role if existing is not None else ""
        if existing is None:
            player = pl.add(saga, values)
        else:
            player = existing
            pl.update(existing, values)
            if was == pl.STORYGUIDE and player.role != pl.STORYGUIDE:
                # Their stories have no storyguide now (ADR 0015).
                viewing.free_records(saga, player.id)
        apply_plays(saga, player, values)
        devices = DeviceBook(devices_path(saga.name))
        if values.get("passcode"):
            RemotePasscodes(passcodes_path(saga.name)).note(player, values["passcode"])
            # A new passcode answers the player's ask for one.
            devices.reset_done(player.id)
        if was and was != player.role and _seated(devices, player):
            AuditLog(audit_path(saga.name)).record(
                audit.ROLE_CHANGED, player_id=player.id
            )

    def apply(values: dict[str, Any]) -> Confirm | None:
        promoting = (
            existing is not None
            and existing.role != pl.STORYGUIDE
            and values.get("role") == pl.STORYGUIDE
        )
        seated = _seated(DeviceBook(devices_path(saga.name)), existing)
        if promoting and seated and existing is not None:
            return Confirm(
                f"Make {escape(existing.name)} a storyguide? Within seconds "
                f"{escape(', '.join(seated))} will see everything in the saga "
                "but another storyguide's stories, Secrets included, and may "
                "change any record in it but those.",
                lambda: store(values),
                yes_label="Make Storyguide",
                title="Make Storyguide",
            )
        demoting = (
            existing is not None
            and existing.role == pl.STORYGUIDE
            and values.get("role") != pl.STORYGUIDE
        )
        freed = storyguides.freed_warning(saga, existing.id) if existing else ""
        if demoting and freed and existing is not None:
            return Confirm(
                f"Make {escape(existing.name)} a player again?{freed}",
                lambda: store(values),
                yes_label="Make Player",
                title="Make Player",
            )
        store(values)
        return None

    return Form(
        player_title(existing),
        lambda: [*player_fields(existing), *plays_fields(saga, existing)],
        apply,
        validate=lambda values: player_problem(saga, existing, values),
    )


def _seated(devices: DeviceBook, player: Player | None) -> list[str]:
    """The names of `player`'s devices with a live Remote seat."""
    if player is None:
        return []
    return [
        d.name for d in devices.devices() if d.player_id == player.id and not d.ended
    ]


def delete_player(saga: Saga, player: Player) -> Confirm:
    """Delete a player, after asking."""

    def apply() -> None:
        viewing.free_records(saga, player.id)
        pl.remove(saga, player)
        RemotePasscodes(passcodes_path(saga.name)).forget(player.id)

    return Confirm(
        f"Delete the player {escape(player.name)}?\n\n"
        "They will no longer be able to sign in."
        + storyguides.freed_warning(saga, player.id),
        apply,
    )


def player_ops(saga: Saga) -> SectionOps:
    """Add, Edit and Delete for the saga's players."""
    return SectionOps(
        add=lambda: player_form(saga, None),
        edit=lambda index: player_form(saga, saga.players[index]),
        remove=lambda index: delete_player(saga, saga.players[index]),
        rows=lambda: [player.name for player in saga.players],
    )


# ------------------------------------------------------------ saga sources


def source_title(existing: SagaSource | None) -> str:
    if existing is None:
        return "Add a Saga Source"
    return f"Edit {escape(existing.title or existing.abbreviation)}"


def source_fields(existing: SagaSource | None) -> list[DialogField]:
    """A source of the saga's own: the abbreviation its House Rules cite,
    and its title."""
    return [
        DialogField(
            "abbreviation",
            "Abbreviation",
            "text",
            existing.abbreviation if existing else "",
            required=True,
            placeholder="e.g. HR",
            hint="What its entries cite, as books are cited (DE, HoH:TL...).",
        ),
        DialogField(
            "title",
            "Title",
            "text",
            existing.title if existing else "",
            placeholder="e.g. Our house rules",
        ),
    ]


def source_ops(saga: Saga) -> SectionOps:
    """Add, Edit and Delete for the saga's own sources. A source an entry
    still cites can't be deleted."""

    def form(existing: SagaSource | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            if existing is None:
                sc.add_source(saga, values)
            else:
                sc.update_source(saga, existing, values)

        return Form(
            source_title(existing),
            lambda: source_fields(existing),
            apply,
            validate=lambda values: sc.source_problem(saga, values, existing),
        )

    def remove(index: int) -> Confirm | Refuse:
        source = saga.sources[index]
        citing = hr.citing(saga, source.abbreviation)
        if citing:
            return Refuse(
                "Delete a Saga Source",
                f"{escape(source.abbreviation)} is cited by "
                f"{escape(', '.join(e.name for e in citing))}: change them first.",
            )
        return Confirm(
            f"Delete {escape(source.abbreviation)}?",
            lambda: sc.remove_source(saga, source),
        )

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(saga.sources[index]),
        remove=remove,
        rows=lambda: [source.abbreviation for source in saga.sources],
    )


# ----------------------------------------------------------- books in play

#: A books-in-play form's check for a book is keyed by this and the book.
BOOK_KEY = "book:"


def books_fields(saga: Saga) -> list[DialogField]:
    """A tick for each supplement and saga source, ticked while it is in
    play; the core book is always in play."""
    own = {s.abbreviation: s for s in saga.sources}
    fields = [
        DialogField(
            "_core",
            "Always in play",
            "info",
            f"{sourcebooks.SOURCEBOOKS[sourcebooks.CORE]} ({sourcebooks.CORE})",
        )
    ]
    for book in sc.every_book(saga):
        if book == sourcebooks.CORE:
            continue
        if book in own:
            source = own[book]
            label = f"{source.title or book} ({book}, the saga's own)"
        else:
            label = f"{sourcebooks.SOURCEBOOKS[book]} ({book})"
        fields.append(
            DialogField(BOOK_KEY + book, label, "check", sc.is_in_play(saga, book))
        )
    return fields


def books_form(saga: Saga) -> Form:
    """Edit which books are in play."""

    def apply(values: dict[str, Any]) -> None:
        sc.set_books_in_play(
            saga,
            [
                key.removeprefix(BOOK_KEY)
                for key, ticked in values.items()
                if key.startswith(BOOK_KEY) and ticked
            ],
        )

    return Form("Books in play", lambda: books_fields(saga), apply)


def toggle_book(saga: Saga, book: str) -> Act:
    """Put one supplement or saga source in play, or out of it, leaving
    the others as they are (a card's in-play chip); saved as the books
    form is."""

    def apply() -> None:
        sc.set_books_in_play(
            saga,
            [
                other
                for other in sc.every_book(saga)
                if other != sourcebooks.CORE
                and sc.is_in_play(saga, other) != (other == book)
            ],
        )

    return Act(apply)


# ------------------------------------------------------------- traditions

#: A traditions form's check for a tradition is keyed by this and its id.
TRADITION_KEY = "tradition-"


def traditions_fields(saga: Saga) -> list[DialogField]:
    """A tick for each non-Hermetic tradition whose book is in play, by
    book, ticked while the saga offers it."""
    playing = {t.id for t in traditions.in_play(saga)}
    shown = [t for t in traditions.listed(saga) if t.id in playing]
    if not shown:
        return [
            DialogField(
                "_none",
                "Traditions",
                "info",
                "No book with a tradition is in play.",
            )
        ]
    return [
        DialogField(
            TRADITION_KEY + t.id,
            f"{t.name} ({t.source})",
            "check",
            traditions.is_on(saga, t.id),
        )
        for t in shown
    ]


def apply_traditions(saga: Saga, values: dict[str, Any]) -> None:
    """Turn each listed tradition on or off; one whose book is out of play
    keeps its switch."""
    for key, ticked in values.items():
        if key.startswith(TRADITION_KEY):
            traditions.set_on(saga, key.removeprefix(TRADITION_KEY), bool(ticked))


def toggle_tradition(saga: Saga, tradition_id: str) -> Act:
    """Offer a tradition, or stop offering it (its chip)."""
    return Act(
        lambda: traditions.set_on(
            saga, tradition_id, not traditions.is_on(saga, tradition_id)
        )
    )


def toggle_tradition_book(saga: Saga, book: str) -> Act:
    """Offer every tradition listed under `book`, or, when all already
    are, none of them (its heading's chip)."""

    def apply() -> None:
        under = [
            t for t in traditions.listed(saga) if traditions.book_of(t, saga) == book
        ]
        every = all(traditions.is_on(saga, t.id) for t in under)
        traditions.set_book_on(saga, book, not every)

    return Act(apply)


def traditions_form(saga: Saga) -> Form:
    """Choose the traditions the saga offers."""
    return Form(
        "Traditions offered",
        lambda: traditions_fields(saga),
        lambda values: apply_traditions(saga, values),
    )


# ---------------------------------------------------------------- catalogs


def catalog_title(key: str) -> str:
    return f"Catalog: {escape(sc.CATALOGS[key].label)}"


def catalog_fields(saga: Saga, key: str) -> list[DialogField]:
    """Whether the saga's pickers offer a shared catalog at all."""
    return [
        DialogField(
            "shown",
            "Offered in this saga",
            "check",
            key not in saga.hidden_catalogs,
            hint="Off: its pickers list only the saga's own entries (F3 in "
            "a picker shows the others). Entries already on a record stay.",
        ),
    ]


def catalog_ops(saga: Saga) -> SectionOps:
    """Edit for each shared catalog, in sc.CATALOGS order."""
    keys = list(sc.CATALOGS)

    def edit(index: int) -> Form:
        key = keys[index]
        return Form(
            catalog_title(key),
            lambda: catalog_fields(saga, key),
            lambda values: sc.set_catalog_shown(saga, key, bool(values["shown"])),
        )

    return SectionOps(edit=edit, rows=lambda: [sc.CATALOGS[key].label for key in keys])


# --------------------------------------------------------- hidden entries


def hide_entry_fields(key: str | None) -> list[DialogField]:
    """Which catalog to hide an entry of (the entry is chosen next)."""
    return [
        DialogField(
            "catalog",
            "Catalog",
            "select",
            key or next(iter(sc.CATALOGS)),
            options=[(c.label, c.key) for c in sc.CATALOGS.values()],
            hint="The entry is chosen next. The saga's pickers leave it "
            "out, as if its book were out of play.",
        ),
    ]


def hideable(saga: Saga, key: str) -> list[Any]:
    """The shared entries of catalog `key` not hidden yet, by name: every
    one, whatever its book (what's out of play is the point here)."""
    hidden = set(saga.hidden_entries.get(key, ()))
    entries = sc.CATALOGS[key].shared()
    return sorted((e for e in entries if e.id not in hidden), key=lambda e: e.name)


def entry_choice(entry: Any) -> Choice:
    source = getattr(entry, "source", "")
    label = f"{entry.name}  [{source}]" if source else entry.name
    return Choice(escape(label), entry.id, search=source)


def hide_entry_choose(saga: Saga, key: str) -> Choose:
    """Choose the entry of catalog `key` to hide, and hide it."""
    return Choose(
        f"Hide an Entry: {escape(sc.CATALOGS[key].label)}",
        lambda: [entry_choice(entry) for entry in hideable(saga, key)],
        lambda entry_id: sc.hide_entry(saga, key, entry_id),
        empty="Every entry is hidden already.",
    )


def hidden_ops(
    saga: Saga, chosen_key: Callable[[], str | None] = lambda: None
) -> SectionOps:
    """Hide one more shared entry (which catalog, then which entry), or
    offer a hidden one again, in sc.hidden_entries order. `chosen_key` is
    the catalog the Hide form starts at."""

    def add() -> Form:
        return Form(
            "Hide a Catalog Entry",
            lambda: hide_entry_fields(chosen_key()),
            lambda values: hide_entry_choose(saga, values["catalog"]),
            save_label="Next",
        )

    def remove(index: int) -> Confirm:
        key, entry = sc.hidden_entries(saga)[index]
        return Confirm(
            f"Offer {escape(entry.name)} again?",
            lambda: sc.show_entry(saga, key, entry.id),
            yes_label="Offer again",
        )

    return SectionOps(
        add=add,
        remove=remove,
        rows=lambda: [entry.name for _, entry in sc.hidden_entries(saga)],
    )
