"""Shared types, constants and the Modifier record every model uses."""

from __future__ import annotations

import re
from dataclasses import dataclass, fields
from typing import Any, Literal, NotRequired, TypedDict, cast, get_args

from ..totals import validate_modifier_type

#: A Mythic Companion is a companion with a Free Mythic Companion Virtue
#: (DE ch. 4): it counts as a companion except where Virtues and Flaws are
#: chosen (see COMPANION_TYPES).
CharacterType = Literal["magus", "companion", "mythic companion", "grog"]
#: The character types that count as a companion (Covenant Inhabitants).
COMPANION_TYPES: tuple[str, ...] = ("companion", "mythic companion")


def as_character_type(value: str) -> CharacterType:
    """`value` as a character type, or ValueError saying which is unknown."""
    if value not in get_args(CharacterType):
        raise ValueError(f"unknown character type {value!r}")
    return cast(CharacterType, value)


VirtueFlawType = Literal["Virtue", "Flaw"]
#: A character catalog entry's type: Qualities and Inferiorities are the
#: non-human counterparts of Virtues and Flaws (RoP:Magic magic characters,
#: HoH:Mystery Cults animals and heartbeasts).
CharacterVirtueFlawType = Literal["Virtue", "Flaw", "Quality", "Inferiority"]
VirtueFlawTier = Literal["Free", "Minor", "Major"]
BoonHookType = Literal["Boon", "Hook"]
Handedness = Literal["right", "left", "ambidextrous"]
FatigueLevel = Literal["fresh", "winded", "weary", "tired", "dazed", "unconscious"]


class SetChange(TypedDict):
    """Set `after` at `path` within a record, keeping `before` (and
    `absent` when the key was new, so undoing takes it out again)."""

    op: Literal["set"]
    record: str
    id: str
    path: list[Any]
    before: Any
    after: Any
    absent: NotRequired[bool]


class AppendChange(TypedDict):
    """Append `value` to the list at `path` within a record."""

    op: Literal["append"]
    record: str
    id: str
    path: list[Any]
    value: Any


class ReasonChange(TypedDict):
    """Give a record's attitude toward `covenant_id` a reason (a Reason's
    fields)."""

    op: Literal["reason"]
    record: str
    id: str
    covenant_id: str
    reason: dict[str, Any]


#: One change the yearly step made (world_turns.py), kept with the saga
#: so deleting its entry undoes it.
Change = SetChange | AppendChange | ReasonChange


#: Display order for the Fatigue Levels track on the character sheet, from
#: least to most fatigued -- Fresh -> Winded -> Weary -> Tired -> Dazed ->
#: Unconscious. Not enforced anywhere (see FatigueLevel), just the order a
#: picker or display should list them in.
FATIGUE_LEVELS: tuple[FatigueLevel, ...] = (
    "fresh",
    "winded",
    "weary",
    "tired",
    "dazed",
    "unconscious",
)

# Point magnitude for each tier, per the core rules: Major Virtues cost, and
# Major Flaws grant, three points; Minor is one point; Free is zero either
# way. A catalog entry's `cost` sign follows `type` (positive for a Virtue's
# cost, negative for a Flaw's grant) but must match this magnitude for its
# `tier` -- enforced in VirtueFlawDef.__post_init__ so a typo in the catalog
# JSON fails loudly at load time instead of silently giving a wrong total.
VIRTUE_FLAW_TIER_COST: dict[str, int] = {"Free": 0, "Minor": 1, "Major": 3}

#: The side of the ledger each character catalog type falls on: a Quality
#: is bought like a Virtue and listed with them, an Inferiority with Flaws.
VIRTUE_FLAW_SIDE: dict[str, VirtueFlawType] = {
    "Virtue": "Virtue",
    "Quality": "Virtue",
    "Flaw": "Flaw",
    "Inferiority": "Flaw",
}

#: The kinds of character a Virtue/Flaw can be restricted to
#: (VirtueFlawDef.audience); an entry with no audience is for anyone. All
#: but the last are non-human; "mythic companion" marks the Free Virtues
#: that make a character a Mythic Companion (Devil Child, Nephilim...).
VIRTUE_FLAW_AUDIENCES: tuple[str, ...] = (
    "faerie",
    "magic being",
    "corrupted beast",
    "animal",
    "mythic companion",
)


def known_fields(cls: type, data: dict[str, Any]) -> dict[str, Any]:
    """`data` filtered down to keys that are still fields of `cls`, so
    `cls(**known_fields(cls, data))` tolerates a stale key from an older save
    (a field since removed) instead of raising a TypeError."""
    names = {f.name for f in fields(cls)}
    return {k: v for k, v in data.items() if k in names}


#: The heading older saves and packs wrote a record's secrets under, at the
#: end of its summary or notes; a record now keeps them in `secrets`.
SECRETS_HEADING = "Secrets"

_SECRETS_LINE = re.compile(r"(?:\A|\n\s*\n)[ \t]*\**Secrets:?\**[ \t]*\n")

#: The line the book packs put in a covenant's notes to point at the
#: secrets under it; with them moved out, it points at nothing.
_SECRETS_POINTER = "What the players do not know."


def split_secrets(text: str) -> tuple[str, str]:
    """`text` before a line reading only "Secrets" (after a blank line,
    or at the start), and what follows it; `text` and "" without one."""
    found = _SECRETS_LINE.search(text)
    if found is None:
        return text, ""
    return text[: found.start()].rstrip(), text[found.end() :].strip()


@dataclass
class Secret:
    """One of a record's Secrets: a short title, its words, and the season
    and year the storyguide revealed it to the troupe (no year: not
    revealed). Only the storyguide reads one not revealed (viewing.py)."""

    title: str = ""
    text: str = ""
    revealed_year: int | None = None
    revealed_season: str = ""

    @property
    def revealed(self) -> bool:
        return self.revealed_year is not None

    @classmethod
    def from_dict(cls, data: object, record: str = "") -> Secret:
        if not isinstance(data, dict):
            raise ValueError(f"{record}: a secret should be a record, not {data!r}.")
        d = known_fields(cls, cast(dict[str, Any], data))
        for key in ("title", "text", "revealed_season"):
            if not isinstance(d.get(key, ""), str):
                raise ValueError(f"{record}: a secret's {key} should be words.")
        year = d.get("revealed_year")
        if year is not None and (not isinstance(year, int) or isinstance(year, bool)):
            raise ValueError(f"{record}: a secret's revealed year should be a number.")
        return cls(**d)


def read_secrets(value: object, record: str = "") -> list[Secret]:
    """A record's saved secrets as a list: an older save's words (one
    untitled secret, none when blank) or the list itself."""
    if value is None or isinstance(value, str):
        return [Secret(text=value.strip())] if value and value.strip() else []
    if isinstance(value, list):
        return [
            v if isinstance(v, Secret) else Secret.from_dict(v, record)
            for v in cast(list[object], value)
        ]
    raise ValueError(f"{record}: its secrets should be a list, not {value!r}.")


def secret_words(secrets: list[Secret]) -> str:
    """Every secret's words, a blank line between: what a pack adds to,
    and what Find looks in."""
    return "\n\n".join(
        part
        for s in secrets
        if (part := "\n".join(w for w in (s.title, s.text) if w.strip()).strip())
    )


def as_secrets(text: str) -> list[Secret]:
    """`text` as a record's secrets: one untitled secret, none when blank
    (how a pack writes what a book says is secret)."""
    return [Secret(text=text.strip())] if text.strip() else []


def move_secrets(data: dict[str, Any], *keys: str) -> dict[str, Any]:
    """`data` (a record as saved) with what follows a Secrets heading in
    each of its `keys` moved to its secrets, and its secrets read as a
    list (read_secrets): an older save's words are one untitled secret,
    the words moved joining it (or, after a list, a secret of their own)."""
    saved = data.get("secrets")
    found = [saved if isinstance(saved, str) else ""]
    for key in keys:
        if isinstance(data.get(key), str):
            shown, hidden = split_secrets(data[key])
            if hidden:
                shown = "\n\n".join(
                    part
                    for part in re.split(r"\n[ \t]*\n", shown)
                    if part.strip() != _SECRETS_POINTER
                )
            data[key] = shown
            found.append(hidden)
    words = "\n\n".join(part for part in found if part.strip())
    record = str(data.get("name") or data.get("id") or "a record")
    if isinstance(saved, list):
        data["secrets"] = read_secrets(saved, record) + read_secrets(words, record)
    else:
        data["secrets"] = read_secrets(words, record)
    return data


SEASONS: tuple[str, ...] = ("Spring", "Summer", "Autumn", "Winter")

#: The four realms an aura or a power can belong to (DE Chapter Twelve).
REALMS: tuple[str, ...] = ("Magic", "Divine", "Faerie", "Infernal")

#: The 8 "Laboratory Characteristics" (ArM5 Covenants, Chapter 9) -- unlike human
#: Characteristics these start at 0 and are cheap to change. Each name here
#: doubles as a LabCharacteristics field name and a `lab_characteristic`
#: Modifier's target.
LAB_CHARACTERISTICS: tuple[str, ...] = (
    "size",
    "refinement",
    "general_quality",
    "upkeep",
    "safety",
    "warping",
    "health",
    "aesthetics",
)
#: What a laboratory Virtue or Flaw may ask for as it is added: a whole
#: number its effect is read from ("intelligence"), and a grog standing in
#: for it ("servant": the grog's id; the grog's Intelligence is used).
LAB_VF_PARAMETERS: tuple[str, ...] = ("servant", "intelligence", "illusory", "cost")
ABILITY_CATEGORIES: tuple[str, ...] = (
    "General",
    "Academic",
    "Martial",
    "Arcane",
    "Supernatural",
    # A hedge tradition's Arts (Hedge Magic): learned like Supernatural
    # Abilities, advanced on the Ability xp table.
    "Hedge Art",
)
#: The Ability categories that are supernatural powers: a Virtue grants
#: them, and they mark their holder as more than mundane.
SUPERNATURAL_CATEGORIES: tuple[str, ...] = ("Supernatural", "Hedge Art")
#: The xp tables an Ability can advance on: the Ability table (5 xp a
#: step), or the Art table (1 xp a step) that Accelerated Abilities and
#: most hedge Arts use (Hedge Magic RE, Ch. 1).
XP_TABLES: tuple[str, ...] = ("ability", "art")


@dataclass
class Modifier:
    """A structured effect a Virtue/Flaw has on a Total or resource flow.

    `applies_to` names a modifier type from totals.MODIFIER_TYPES (e.g.
    "lab_total", "casting_total", "study_total", "aging_roll", "art_xp_gain").
    `target` optionally narrows the modifier to a specific Art/Ability named
    by one of the catalog entry's `parameters` (e.g. "{art}"); a target
    ending in "*" covers every name it begins ("Craft: *").

    `activity` optionally narrows it further to one specific activity within
    that type -- e.g. two modifiers both applying to "lab_total" but one
    scoped to "invent_spells" and the other to "extract_vis", each with its
    own amount. A single Virtue/Flaw can carry several such modifiers (it's
    a list on VirtueFlawDef), so different amounts for different activities
    from the same source are just multiple Modifier entries, disambiguated
    by `activity`. See totals.ACTIVITIES_BY_TYPE for the valid activities
    per type; both fields are validated against that registry so a typo or
    an unmodeled type/activity fails loudly at load time rather than
    silently disappearing from a future totals calculation.
    """

    applies_to: str
    amount: float | None = None
    multiplier: float | None = None
    target: str | None = None
    activity: str | None = None
    #: Applies only when the instance's parameters have these values
    #: ({"realm": "divine"}): an entry whose effect depends on a choice
    #: (Student of (Realm), a Faerie Blood's heritage) carries one modifier
    #: per choice.
    when: dict[str, str] | None = None
    #: The amount is read from the instance's parameter of this name, a
    #: whole number, divided by `amount_divisor` and rounded up: Servant's
    #: "+(servant's Intelligence / 2, rounding up) Safety" is
    #: amount_param "intelligence", amount_divisor 2. Used instead of
    #: `amount`; an instance that hasn't entered the number gets nothing.
    amount_param: str | None = None
    amount_divisor: int = 1

    def __post_init__(self) -> None:
        validate_modifier_type(self.applies_to, self.activity)
        if self.amount_param is not None and self.amount is not None:
            raise ValueError(
                f"A modifier has both an amount and amount_param "
                f"{self.amount_param!r}; it reads one or the other"
            )
        if self.amount_divisor < 1:
            raise ValueError(
                f"amount_divisor must be 1 or more, not {self.amount_divisor}"
            )


#: What an experimental effect came from: the Extraordinary Results
#: chart's side effect (5-6), modified effect (11), or the storyguide's
#: change to the creation on a special result (9).
EXPERIMENTAL_KINDS: tuple[str, ...] = ("side", "modified", "special")
_KIND_LABELS = {"side": "Side effect", "modified": "Modified effect"}


@dataclass
class ExperimentalEffect:
    """One thing an experiment left on its creation (a spell, an instilled
    effect, a bond power, a Longevity Ritual), "warts and all". The level
    never changes and no requisite is added, whatever it does.

    `result` is the sub-table's wording ("major side benefit"); the
    storyguide's `description` says what it actually is. A modified effect
    may give the creation a new Range, Duration or Target ("" leaves it as
    it was) or change its potency by whole steps (each step moves the Lab
    Total behind it by 5; a Longevity Ritual's modifier by 1). `fatal` marks
    a fatal flaw. `magic_theory` is the experimenter's Magic Theory that
    season, for recreating the creation without its flaws."""

    kind: str = "side"
    result: str = ""
    description: str = ""
    range: str = ""
    duration: str = ""
    target: str = ""
    potency: int = 0
    fatal: bool = False
    year: int | None = None
    season: str = ""
    magic_theory: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | str) -> ExperimentalEffect:
        if isinstance(data, str):
            # Older saves kept a label ("Side effect: minor flaw").
            kind, _, result = data.partition(": ")
            for key, label in _KIND_LABELS.items():
                if kind == label:
                    return cls(kind=key, result=result.strip())
            return cls(kind="special", result=data.strip())
        return cls(**known_fields(cls, data))

    @property
    def label(self) -> str:
        """ "Side effect: minor flaw", or the result alone."""
        kind = _KIND_LABELS.get(self.kind, "")
        return f"{kind}: {self.result}" if kind and self.result else self.result


def experimental_effects(items: Any) -> list[ExperimentalEffect]:
    """A saved list of experimental effects (records, or an older save's
    labels) as records."""
    return [
        item
        if isinstance(item, ExperimentalEffect)
        else ExperimentalEffect.from_dict(item)
        for item in items or []
    ]


def _validate_vf_tier_cost(id_: str, tier: str, cost: float) -> None:
    """Shared by VirtueFlawDef and LabVirtueFlawDef: cost's magnitude must
    match VIRTUE_FLAW_TIER_COST[tier] (0/1/3 for Free/Minor/Major)."""
    if tier not in VIRTUE_FLAW_TIER_COST:
        raise ValueError(
            f"Unknown tier {tier!r} for {id_!r}; "
            f"must be one of {sorted(VIRTUE_FLAW_TIER_COST)}"
        )
    expected_magnitude = VIRTUE_FLAW_TIER_COST[tier]
    if abs(cost) != expected_magnitude:
        raise ValueError(
            f"{id_!r} is {tier!r} tier (should cost "
            f"{expected_magnitude} points) but has cost {cost!r}"
        )
