"""Resolve Twilight (More on Aging & Warping): the storyguide's choice of a
Twilight's effects, applied (DE pp. 229-230). A comprehended Twilight
gives a good Twilight Scar and xp in an Art, Magic Theory or Enigmatic
Wisdom (twice the Warping Points gained), a Hermetic or Supernatural
Virtue (Minor from 7 points, Major from 11), or a spell of that many
magnitudes; a Twilight not comprehended gives a bad scar and the same
taken away: xp lost, a Flaw (Minor from 7, Major from 10), or spells lost.
The scar is kept on Aging & Warping and the whole is written in the
Diary."""

from __future__ import annotations

from typing import Any

from .. import catalog, diaries
from ..arts import ARTS
from ..commands import Form, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import (
    Ability,
    ArtScore,
    Character,
    KnownSpell,
    Saga,
    VirtueFlawDef,
    VirtueFlawInstance,
)
from ..rules.rounding import round_up

TITLE = "Resolve Twilight"
#: Resolve Twilight's own help page.
HELP_ID = "resolve-twilight"
SOURCE = "Ars Magica Definitive Edition, Effects of Twilight, pp. 229-230"

XP, VIRTUE, SPELL, SCAR_ONLY = "xp", "virtue", "spell", "scar"
EFFECTS: list[tuple[str, str]] = [
    ("Experience (twice the points, gained or lost)", XP),
    ("A Virtue or Flaw (7 points or more)", VIRTUE),
    ("A spell (learned or lost)", SPELL),
    ("Only the scar", SCAR_ONLY),
]
#: What Twilight's experience may go to, besides the Arts.
KNOWLEDGE = ("Magic Theory", "Enigmatic Wisdom")
XP_PER_POINT = 2
#: The Warping Points a Virtue or Flaw needs: Minor from 7; a Major Virtue
#: from 11 ("more than ten"), a Major Flaw from 10 (DE p. 230).
MINOR_FROM, MAJOR_VIRTUE_FROM, MAJOR_FLAW_FROM = 7, 11, 10


def tier_for(points: int, *, comprehended: bool) -> str:
    """The tier of Virtue (or Flaw) the points give, or "" for none."""
    if points < MINOR_FROM:
        return ""
    major = MAJOR_VIRTUE_FROM if comprehended else MAJOR_FLAW_FROM
    return "Major" if points >= major else "Minor"


def _offered(entry: VirtueFlawDef) -> bool:
    return entry.category in ("Hermetic", "Supernatural") and not entry.parameters


def virtue_options(*, comprehended: bool) -> list[tuple[str, str]]:
    side = "Virtue" if comprehended else "Flaw"
    return [
        (f"{escape(e.name)} ({e.tier} {e.category})", e.id)
        for e in catalog.virtue_flaws_by_name(catalog.load_virtue_flaw_catalog())
        if e.side == side and _offered(e)
    ]


def magnitude(level: int | None) -> int:
    """A spell's magnitude; a spell of no set level (a general one) is 1."""
    return max(1, round_up((level or 0) / 5))


def _comprehended(values: dict[str, Any]) -> bool:
    return bool(values.get("comprehended"))


def _effect(kind: str, *, comprehended: bool | None = None) -> Any:
    return lambda v: (
        (v.get("effect") == kind)
        and (comprehended is None or _comprehended(v) == comprehended)
    )


def fields(saga: Saga, character: Character) -> list[DialogField]:
    known = [
        (escape(spell.name), k.spell_id)
        for k in character.spells_known
        if (spell := catalog.find_spell(saga, k.spell_id)) is not None
    ]
    return [
        DialogField(
            "comprehended",
            "Comprehended",
            "check",
            False,
            hint="A Twilight understood marks the maga well; one not, badly.",
        ),
        DialogField(
            "points",
            "Warping Points gained",
            "int",
            2,
            hint="In all: those that brought on the Twilight and the simple "
            "die more (DE p. 229).",
        ),
        DialogField("effect", "Effect", "select", XP, options=EFFECTS),
        DialogField(
            "art",
            "Art or Ability",
            "select",
            "Magic Theory",
            options=[(a, a) for a in (*KNOWLEDGE, *ARTS)],
            show_if=_effect(XP),
        ),
        DialogField(
            "virtue",
            "Virtue gained",
            "select",
            None,
            options=virtue_options(comprehended=True),
            allow_blank=True,
            placeholder="(choose)",
            show_if=_effect(VIRTUE, comprehended=True),
        ),
        DialogField(
            "flaw",
            "Flaw gained",
            "select",
            None,
            options=virtue_options(comprehended=False),
            allow_blank=True,
            placeholder="(choose)",
            show_if=_effect(VIRTUE, comprehended=False),
        ),
        DialogField(
            "spell",
            "Spell learned",
            "select",
            None,
            options=[
                (f"{escape(s.name)} ({s.technique[:2]}{s.form[:2]} {s.level})", s.id)
                for s in catalog.load_spell_catalog()
            ],
            allow_blank=True,
            placeholder="(choose)",
            show_if=_effect(SPELL, comprehended=True),
            hint="The storyguide's choice, of as many magnitudes as the points; "
            "she need not be able to cast it.",
        ),
        DialogField(
            "lost_spell",
            "Spell lost",
            "select",
            None,
            options=known,
            allow_blank=True,
            placeholder="(choose)",
            show_if=_effect(SPELL, comprehended=False),
            hint="Spells of as many magnitudes in all as the points: resolve "
            "again, or delete the rest on the Spells tab.",
        ),
        DialogField(
            "scar",
            "Twilight Scar",
            "area",
            "",
            hint="Something minor and magical: pleasant if comprehended, "
            "annoying if not (DE pp. 229-230).",
        ),
    ]


def problem(values: dict[str, Any]) -> str | None:
    """Why the choice can't be applied (None if it can)."""
    points = values.get("points") or 0
    comprehended = _comprehended(values)
    if points < 1:
        return "Type the Warping Points the Twilight gave."
    effect = values.get("effect")
    if effect == VIRTUE:
        tier = tier_for(points, comprehended=comprehended)
        if not tier:
            return f"A Virtue or Flaw needs {MINOR_FROM} Warping Points or more."
        chosen = values.get("virtue" if comprehended else "flaw")
        if not chosen:
            return "Choose the Virtue." if comprehended else "Choose the Flaw."
        entry = catalog.load_virtue_flaw_catalog_by_id().get(chosen)
        if entry is not None and entry.tier != tier:
            return f"{points} points give a {tier} one, not {entry.tier}."
    if effect == SPELL:
        if comprehended:
            spell = catalog.load_spell_catalog_by_id().get(values.get("spell") or "")
            if spell is None:
                return "Choose the spell learned."
            if magnitude(spell.level) != points:
                return (
                    f"The spell should be of {points} magnitudes; "
                    f"{escape(spell.name)} is of {magnitude(spell.level)}."
                )
        elif not values.get("lost_spell"):
            return "Choose a spell lost."
    return None


def _give_xp(character: Character, name: str, amount: int) -> int:
    """Add (or take, never below 0) `amount` xp; returns the change."""
    if name in ARTS:
        art = character.arts.setdefault(name.lower(), ArtScore())
        change = max(-art.xp, amount)
        art.xp += change
        return change
    ability = next((a for a in character.abilities if a.name == name), None)
    if ability is None:
        if amount <= 0:
            return 0
        ability = Ability(name)
        character.abilities.append(ability)
    change = max(-ability.xp, amount)
    ability.xp += change
    return change


def apply(saga: Saga, character: Character, values: dict[str, Any]) -> list[str]:
    points = int(values.get("points") or 0)
    comprehended = _comprehended(values)
    effect = values.get("effect")
    told: list[str] = []
    if effect == XP:
        name = values.get("art") or "Magic Theory"
        amount = XP_PER_POINT * points
        change = _give_xp(character, name, amount if comprehended else -amount)
        told.append(
            f"{abs(change)} xp {'gained' if change >= 0 else 'lost'} in {name}."
        )
    elif effect == VIRTUE:
        chosen = values.get("virtue" if comprehended else "flaw") or ""
        entry = catalog.load_virtue_flaw_catalog_by_id().get(chosen)
        character.virtues_flaws.append(VirtueFlawInstance(chosen))
        told.append(f"{entry.name if entry else chosen} gained.")
    elif effect == SPELL:
        if comprehended:
            spell_id = values.get("spell") or ""
            spell = catalog.load_spell_catalog_by_id().get(spell_id)
            if not any(k.spell_id == spell_id for k in character.spells_known):
                character.spells_known.append(KnownSpell(spell_id))
            told.append(f"{spell.name if spell else spell_id} learned.")
        else:
            lost = values.get("lost_spell") or ""
            spell = catalog.find_spell(saga, lost)
            character.spells_known = [
                k for k in character.spells_known if k.spell_id != lost
            ]
            told.append(f"{spell.name if spell else lost} forgotten.")
    scar = (values.get("scar") or "").strip()
    if scar:
        aging = character.aging
        aging.twilight_scars = "\n".join(
            line for line in (aging.twilight_scars, scar) if line
        )
        told.append(f"Twilight Scar: {scar}")
    kind = "comprehended" if comprehended else "not comprehended"
    diaries.write(
        saga.current_year,
        saga.current_season,
        "Twilight",
        f"A Twilight {kind} ({points} Warping Points): " + " ".join(told),
        characters=[character],
    )
    return notes(*(escape(t) for t in told), "Written in the Diary.")


def resolve_twilight_form(saga: Saga, character: Character) -> Form:
    return Form(
        f"{TITLE}: {escape(character.name)}",
        lambda: fields(saga, character),
        lambda values: apply(saga, character, values),
        validate=problem,
        help_id=HELP_ID,
    )
