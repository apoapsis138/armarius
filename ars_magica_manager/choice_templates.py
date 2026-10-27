"""Choice Templates: ways to start a character, other than the Definitive
Edition's ready-made characters (character_templates.py), that are a set
of choices. New Character asks for them (forms/choice_templates.py)
before the character is made; it starts In Creation, to be finished on
the Creation Worksheet.

The first are the Definitive Edition's Quick and Easy Virtues and Flaws
(Chapter Three, page 46): a recipe of Virtues and Flaws for a grog, for
four kinds of companion (martial, learned, social, magical) and for a
magus. A recipe sets only Virtues and Flaws; Characteristics and
Abilities are left to the worksheet.

Then the Mythic Companions, one for each status Virtue the books give
(the Definitive Edition's Devil Child, Faerie Doctor, Nephilim and Spirit
Votary, and the supplements' Zahid, Perfectus, Kabbalist, Diabolist,
Summoner, Blood of Heroes and Maestro): the Virtues and Flaws each must
take, its "or a suitable substitute" Flaws as a pick, more Virtues and
Flaws of the player's own, and the minimum Abilities the book gives, put
on the worksheet as xp.

Then the supplements' ready-made companions ("sample"), such as Realms
of Power: The Divine's Byzantine Priest or The Church's Mystic Nun: the
book's age, Characteristics, Virtues and Flaws (ticked, to be left out
one by one), Abilities with their specialties, Personality Traits and
Reputations, with more Virtues and Flaws of the player's own.

Each entry is a Prototype: catalog data copied into a new character as
its choices say. The choices are held to the limits of the entry's
character type, a Strategy picked from LIMITS: a grog's are
grog_templates.limit_problem; a companion's, a Mythic Companion's and a
magus's are here.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field, replace
from functools import lru_cache
from pathlib import Path
from typing import Any

from . import DATA_DIR, catalog, sourcebooks
from . import grog_templates as gt
from .arts import FORMS, TECHNIQUES
from .markup import escape
from .models import (
    Character,
    GrogTemplateDef,
    Saga,
    ScoredTrait,
    VirtueFlawDef,
    VirtueFlawInstance,
    known_fields,
)
from .rules import creation_character as cc
from .rules import creation_characteristics as cch
from .rules import creation_virtues as cv
from .rules import creation_xp as cx
from .rules.vf_eligibility import VirtueFlawChooser
from .rules.xp import ability_xp

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Quick and Easy Virtues "
    "and Flaws, p. 47"
)
CATALOG_PATH = DATA_DIR / "choice_template_catalog.json"
COVENFOLK = "vf_covenfolk"
#: Book abbreviations as the help and summaries name them.
BOOK_NAMES: dict[str, str] = {
    "DE": "Definitive Edition",
    "RoP:D": "Realms of Power: The Divine",
    "RoP:I": "Realms of Power: The Infernal",
    "HoH:TL": "Houses of Hermes: True Lineages",
    "A&A": "Art & Academe",
}
#: An "art" slot's Arts, by its group.
ART_GROUPS: dict[str, tuple[str, ...]] = {"technique": TECHNIQUES, "form": FORMS}


@dataclass
class ChoiceTemplateDef:
    """One entry of choice_template_catalog.json, for a new character of
    `type`. `flaw` ({"tier", "categories"}) is the Flaw every version
    asks for; `statuses` the Social Statuses offered (none listed: any the
    type may take, Covenfolk first). `variants` are the book's versions
    to choose between (under `variant_label`), each a list of `slots`:

    - {"kind": "fixed", "vf_id"}: a Virtue or Flaw always taken;
    - {"kind": "one_of", "label", "vf_ids"}: one of these;
    - {"kind": "ability", "label", "categories" or "names" or "free",
      "vf_ids"}: an Ability of those catalog categories, one of those
      names, or (free) typed in, which each of `vf_ids` ("Puissant
      {ability}") then names;
    - {"kind": "supernatural", "label", "vf_ids"}: a Minor Supernatural
      Virtue that grants an Ability of its own name, which each of
      `vf_ids` then names;
    - {"kind": "art", "label", "group", "param"?, "vf_ids"}: a Technique
      or Form, which each of `vf_ids` names as its `param` ("art");
    - {"kind": "text", "label", "param", "vf_ids"}: typed in, which each
      of `vf_ids` names as its `param` (a Magical Focus's "focus");
    - {"kind": "virtue" or "flaw", "label", "tier", "categories"?,
      "default"?}: any Virtue (or Flaw) of that tier and those categories
      the type may take, `default` chosen to start with (the book's Flaw,
      where it allows "a suitable substitute").

    A slot may carry a `hint` for its field. `more_virtues` and
    `more_flaws` are how many other Virtues and Flaws of the player's own
    the form offers; `abilities` ({"name", "score"} each, "{area}" and the
    like asked for) the minimum Abilities the book gives."""

    id: str
    name: str
    type: str = "companion"
    kind: str = "quick"
    book: str = "DE"
    page: int = 0
    concept: str = ""
    flaw: dict[str, Any] = field(default_factory=dict)
    statuses: list[str] = field(default_factory=list)
    variant_label: str = ""
    variants: list[dict[str, Any]] = field(default_factory=list)
    more_virtues: int = 0
    more_flaws: int = 0
    abilities: list[dict[str, Any]] = field(default_factory=list)
    #: A book's ready-made character ("sample"): its age, Characteristics,
    #: own Virtues and Flaws ({"vf_id", "params", "note"?}, taken unless
    #: unticked), Native Language (an Ability's name), Personality Traits
    #: and Reputations ([name, score] each). Its `abilities` carry the
    #: book's "(xp)" toward the next score and a specialty.
    age: int = 0
    characteristics: dict[str, int] = field(default_factory=dict)
    virtues_flaws: list[dict[str, Any]] = field(default_factory=list)
    native: str = ""
    traits: list[list[Any]] = field(default_factory=list)
    reputations: list[list[Any]] = field(default_factory=list)
    notes: str = ""
    #: Where this entry differs from the page's text, and why.
    fixes: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChoiceTemplateDef:
        return cls(**known_fields(cls, data))


@dataclass
class Choices:
    """What the player chose: the variant (an index), the Social Status
    and the Flaw (vf_ids), each of the variant's slots' picks in order
    ("" for a fixed slot: a vf_id, an Ability's or Art's name, or text),
    other Virtues and Flaws, whether to put the book's minimum Abilities on
    the worksheet, and the names those leave blank ("area")."""

    variant: int = 0
    status: str = ""
    flaw: str = ""
    picks: list[str] = field(default_factory=list)
    more: list[VirtueFlawInstance] = field(default_factory=list)
    abilities: bool = True
    blanks: dict[str, str] = field(default_factory=dict)
    #: A sample's: the indexes of its own Virtues and Flaws left out, and
    #: whether to take its Characteristics.
    dropped: set[int] = field(default_factory=set)
    characteristics: bool = True


@lru_cache(maxsize=2)
def _load(path: Path) -> tuple[ChoiceTemplateDef, ...]:
    return tuple(catalog._load_entries(path, ChoiceTemplateDef.from_dict))


def load_catalog(path: Path = CATALOG_PATH) -> list[ChoiceTemplateDef]:
    return list(_load(path))


def templates(saga: Saga | None, character_type: str) -> list[ChoiceTemplateDef]:
    """The templates offered for a new character of `character_type`:
    those whose book is in play."""
    books = sourcebooks.saga_books(saga)
    return [
        t
        for t in load_catalog()
        if t.type == character_type and sourcebooks.in_play(t.book, books)
    ]


def option_label(template: ChoiceTemplateDef) -> str:
    """How New Character's Template list names `template`: a Mythic
    Companion's with its book ("Zahid (RoP:D)")."""
    if template.kind in ("mythic", "sample"):
        return f"{template.name} ({template.book})"
    return template.name


def find(template_id: str | None) -> ChoiceTemplateDef | None:
    if not template_id:
        return None
    return next((t for t in load_catalog() if t.id == template_id), None)


def variants(template: ChoiceTemplateDef) -> list[dict[str, Any]]:
    return template.variants or [{"name": "", "slots": []}]


def slots(template: ChoiceTemplateDef, variant: int) -> list[dict[str, Any]]:
    return list(variants(template)[variant].get("slots", []))


# -- what a choice may be --


def _blank(character_type: str) -> Character:
    return Character(id="", name="", type=character_type)  # type: ignore[arg-type]


def _chooser(saga: Saga | None, character_type: str) -> VirtueFlawChooser:
    return VirtueFlawChooser.for_character(
        _blank(character_type), sourcebooks.saga_books(saga)
    )


def _sorted(entries: list[VirtueFlawDef]) -> list[VirtueFlawDef]:
    return sorted(entries, key=lambda e: e.name)


def status_options(
    saga: Saga | None, template: ChoiceTemplateDef
) -> list[VirtueFlawDef]:
    """The Social Statuses offered: the template's, or every one its type
    may take, Covenfolk first."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    if template.statuses:
        return [by_id[s] for s in template.statuses if s in by_id]
    chooser = _chooser(saga, template.type)
    found = _sorted(
        [
            e
            for e in catalog.load_virtue_flaw_catalog()
            if e.category == "Social Status"
            and not e.parameters
            and not chooser.refusal(e)
        ]
    )
    return sorted(found, key=lambda e: e.id != COVENFOLK)


def default_status(saga: Saga | None, template: ChoiceTemplateDef) -> str:
    found = status_options(saga, template)
    return found[0].id if found else ""


def flaw_options(saga: Saga | None, template: ChoiceTemplateDef) -> list[VirtueFlawDef]:
    """The Flaws of the template's `flaw` tier and categories its type may
    take (those naming nothing, which the form can't ask for)."""
    chooser = _chooser(saga, template.type)
    tier = template.flaw.get("tier", "Major")
    categories = set(template.flaw.get("categories", ()))
    return _sorted(
        [
            e
            for e in catalog.load_virtue_flaw_catalog()
            if e.side == "Flaw"
            and e.tier == tier
            and categories & {e.category, *e.extra_categories}
            and not e.parameters
            and not chooser.refusal(e)
        ]
    )


def ability_options(slot: dict[str, Any]) -> list[str]:
    """An "ability" slot's Abilities: its names, or the catalog's Abilities
    of its categories that name nothing (none for a typed one)."""
    if slot.get("names"):
        return list(slot["names"])
    wanted = set(slot.get("categories", ()))
    return sorted(
        a.name
        for a in catalog.load_ability_catalog()
        if a.category in wanted and not a.parameters
    )


def supernatural_options(
    saga: Saga | None, character_type: str = "companion"
) -> list[VirtueFlawDef]:
    """The Minor Supernatural Virtues that grant an Ability of their own
    name, which `character_type` may take."""
    chooser = _chooser(saga, character_type)
    granted = {
        a.name
        for a in catalog.load_ability_catalog()
        if a.category == "Supernatural" and not a.parameters
    }
    return _sorted(
        [
            e
            for e in catalog.load_virtue_flaw_catalog()
            if e.side == "Virtue"
            and e.tier == "Minor"
            and e.category == "Supernatural"
            and e.name in granted
            and not chooser.refusal(e)
        ]
    )


def one_of_options(
    saga: Saga | None, slot: dict[str, Any], character_type: str = "companion"
) -> list[VirtueFlawDef]:
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    chooser = _chooser(saga, character_type)
    return [
        by_id[i] for i in slot["vf_ids"] if i in by_id and not chooser.refusal(by_id[i])
    ]


def tier_options(
    saga: Saga | None, slot: dict[str, Any], character_type: str
) -> list[VirtueFlawDef]:
    """A "virtue" or "flaw" slot's choices: every entry of its side, tier
    and categories (any, if it names none) `character_type` may take,
    naming nothing; its `default` is offered even if it names something."""
    side = "Virtue" if slot["kind"] == "virtue" else "Flaw"
    categories = set(slot.get("categories", ()))
    chooser = _chooser(saga, character_type)
    found = _sorted(
        [
            e
            for e in catalog.load_virtue_flaw_catalog()
            if e.side == side
            and e.tier == slot["tier"]
            and (not categories or categories & {e.category, *e.extra_categories})
            and (not e.parameters or e.id == slot.get("default"))
            and not chooser.refusal(e)
        ]
    )
    return sorted(found, key=lambda e: e.id != slot.get("default"))


# -- the minimum Abilities --


def ability_rows(
    template: ChoiceTemplateDef, values: dict[str, str] | None = None
) -> cx.XpRows:
    """The book's Abilities as (name, xp) rows, with any "(xp)" toward the
    next score, the names it leaves blank filled from `values` where
    given."""
    rows = tuple(
        (a["name"], ability_xp(a["score"]) + a.get("xp", 0)) for a in template.abilities
    )
    return tuple(cx.fill_template(rows, values)) if values else rows


def native_name(template: ChoiceTemplateDef, values: dict[str, str]) -> str:
    """A sample's Native Language, its blank filled from `values`."""
    if not template.native:
        return ""
    return cx.fill_template(((template.native, 0),), values)[0][0]


def blanks(template: ChoiceTemplateDef) -> list[str]:
    """The names the minimum Abilities leave to the player ("area")."""
    return cx.template_blanks(ability_rows(template))


def abilities_text(template: ChoiceTemplateDef) -> str:
    """ "Curse-Throwing 4, Dowsing 1 (55 xp)"."""
    listed = ", ".join(f"{a['name']} {a['score']}" for a in template.abilities)
    total = sum(xp for _, xp in ability_rows(template))
    return f"{listed} ({total} xp)"


# -- the chosen Virtues and Flaws --


def _named(slot: dict[str, Any], value: str, param: str) -> list[VirtueFlawInstance]:
    return [
        VirtueFlawInstance(vf_id, {slot.get("param", param): value.lower()})
        for vf_id in slot.get("vf_ids", ())
    ]


def chosen(template: ChoiceTemplateDef, choices: Choices) -> list[VirtueFlawInstance]:
    """Every Virtue and Flaw `choices` give: the Social Status, the
    variant's slots in order, then the Flaw. A slot left blank gives
    nothing."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    found = [VirtueFlawInstance(choices.status)] if choices.status else []
    found += [
        VirtueFlawInstance(vf["vf_id"], dict(vf.get("params", {})))
        for n, vf in enumerate(template.virtues_flaws)
        if n not in choices.dropped
    ]
    for n, slot in enumerate(slots(template, choices.variant)):
        pick = (choices.picks[n] if n < len(choices.picks) else "").strip()
        kind = slot["kind"]
        if kind == "fixed":
            found.append(
                VirtueFlawInstance(slot["vf_id"], dict(slot.get("params", {})))
            )
        elif not pick:
            continue
        elif kind in ("one_of", "virtue", "flaw"):
            found.append(VirtueFlawInstance(pick))
        elif kind == "ability":
            found += _named(slot, pick, "ability")
        elif kind == "art":
            found += _named(slot, pick, "art")
        elif kind == "text":
            found += _named(slot, pick, "text")
        elif kind == "supernatural" and pick in by_id:
            found.append(VirtueFlawInstance(pick))
            found += _named(slot, by_id[pick].name, "ability")
    if choices.flaw:
        found.append(VirtueFlawInstance(choices.flaw))
    return found + list(choices.more)


# -- the limits, by character type --


def _points(count: int, side: str) -> str:
    return f"{count} {side} point{'' if count == 1 else 's'}"


def _book_limits(
    character_type: str,
    chosen: Sequence[VirtueFlawInstance],
    statuses: int = 1,
    book_repeats: frozenset[str] = frozenset(),
) -> str | None:
    """A companion's or magus's limits (Definitive Edition, Chapter
    Three), or None if `chosen` keeps to them. Fewer Virtue points than
    Flaw points is allowed: the worksheet shows the points left to
    balance."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    character = _blank(character_type)
    character.virtues_flaws = list(chosen)
    t = cv.tally(character)
    entries = [by_id[vf.vf_id] for vf in chosen if vf.vf_id in by_id]
    gifted = character_type == "magus" or any(e.id in catalog.GIFT_IDS for e in entries)
    hermetic = [e.name for e in entries if catalog.needs_the_gift(e)]
    if hermetic and not gifted:
        return f"Hermetic Virtues and Flaws need The Gift: {', '.join(hermetic)}."
    if t.major_hermetic_virtues > 1:
        return "At most one Major Hermetic Virtue."
    most_points = cv.max_flaw_points(character)
    if t.flaw_points > most_points:
        return f"At most {most_points} points of Flaws: {t.flaw_points} chosen."
    most_minor = cv.max_minor_flaws(character)
    if t.minor_flaws > most_minor:
        return f"At most {most_minor} Minor Flaws: {t.minor_flaws} chosen."
    if t.virtue_points > t.flaw_points:
        return (
            f"{_points(t.virtue_points, 'Virtue')} but only "
            f"{_points(t.flaw_points, 'Flaw')}: take another Flaw or leave a "
            "Virtue out."
        )
    if not 1 <= len(t.social_statuses) <= statuses:
        allowed = (
            "One Social Status" if statuses == 1 else f"1 to {statuses} Social Statuses"
        )
        return f"{allowed}: " + (", ".join(t.social_statuses) or "none") + " chosen."
    repeated = [name for name in t.repeated if name not in book_repeats]
    if repeated:
        return f"Taken more often than the book allows: {', '.join(repeated)}."
    return None


def _mythic_limits(chosen: Sequence[VirtueFlawInstance]) -> str | None:
    """A Mythic Companion's limits (Definitive Edition, Chapter Three,
    Mythic Companions): one status Virtue, no Gift, at most ten points of
    Flaws (five Minor), each worth two points of Virtues, plus the free
    Minor, 21 at most. Fewer Virtue points is allowed, as above."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    character = _blank("mythic companion")
    character.virtues_flaws = list(chosen)
    t = cv.tally(character)
    ids = [vf.vf_id for vf in chosen]
    statuses = [i for i in ids if i in cc.mythic_status_ids()]
    if len(statuses) != 1:
        return f"One Mythic Companion status Virtue: {len(statuses)} chosen."
    gift = [by_id[i].name for i in ids if i in catalog.GIFT_IDS and i in by_id]
    hermetic = [
        by_id[i].name for i in ids if i in by_id and catalog.needs_the_gift(by_id[i])
    ]
    if gift or hermetic:
        return (
            "A Mythic Companion has no Gift, so nothing Hermetic: "
            f"{', '.join(gift + hermetic)}."
        )
    most_points = cv.max_flaw_points(character)
    if t.flaw_points > most_points:
        return f"At most {most_points} points of Flaws: {t.flaw_points} chosen."
    most_minor = cv.max_minor_flaws(character)
    if t.minor_flaws > most_minor:
        return f"At most {most_minor} Minor Flaws: {t.minor_flaws} chosen."
    _, most_virtues = cv.virtue_allowance(character, t.flaw_points)
    if t.virtue_points > most_virtues:
        return (
            f"{_points(t.virtue_points, 'Virtue')} but "
            f"{_points(t.flaw_points, 'Flaw')} allow {most_virtues}: take "
            "another Flaw or leave a Virtue out."
        )
    if t.repeated:
        return f"Taken more often than the book allows: {', '.join(t.repeated)}."
    return None


#: Why `chosen` breaks a character type's limits, or None: the Strategy
#: each template's type picks.
LIMITS: dict[str, Callable[[Sequence[VirtueFlawInstance]], str | None]] = {
    "grog": gt.limit_problem,
    "companion": lambda chosen: _book_limits("companion", chosen),
    "mythic companion": _mythic_limits,
    "magus": lambda chosen: _book_limits("magus", chosen),
}


def limit_problem(
    template: ChoiceTemplateDef, chosen: Sequence[VirtueFlawInstance]
) -> str | None:
    """Why `chosen` breaks the limits of `template`'s type, or None. A
    book's companion may keep the several Social Statuses the book gives
    it (a Mamluk Emir is Emir, Mamluk and Muqta')."""
    if template.kind == "sample" and template.type == "companion":
        return _book_limits(
            "companion",
            chosen,
            max(1, len(book_statuses(template))),
            _book_repeats(template),
        )
    return LIMITS[template.type](chosen)


def _book_repeats(template: ChoiceTemplateDef) -> frozenset[str]:
    """The Virtues and Flaws a book's own character takes more than once
    (the Mystic Nun's two Ability Blocks), which its book allows it."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    ids = [vf["vf_id"] for vf in template.virtues_flaws]
    return frozenset(by_id[i].name for i in ids if ids.count(i) > 1 and i in by_id)


def book_statuses(template: ChoiceTemplateDef) -> list[str]:
    """A template's Social Statuses: the one chosen and those of its own
    Virtues and Flaws."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    own = [
        vf["vf_id"]
        for vf in template.virtues_flaws
        if vf["vf_id"] in by_id and by_id[vf["vf_id"]].category == "Social Status"
    ]
    return template.statuses[:1] + own


# -- a Grogs template played as a companion --

#: Grogs, Chapter 7: a grog template becomes a companion by adding a Story
#: Flaw (Animal Trainer as Companion, page 95).
GROG_COMPANION_SOURCE = "Grogs, Chapter 7, page 95"


def grog_companion_problem(chosen: Sequence[VirtueFlawInstance]) -> str | None:
    """Why a Grogs template can't be played as a companion with `chosen`:
    a companion's limits, and the Story Flaw that makes it one."""
    problem = LIMITS["companion"](chosen)
    if problem:
        return problem
    character = _blank("companion")
    character.virtues_flaws = list(chosen)
    if not cv.tally(character).story_flaws:
        return (
            "A grog template becomes a companion by adding a Story Flaw "
            f"({GROG_COMPANION_SOURCE}): choose one under Another Flaw."
        )
    return None


def after_grog_apply(character: Character, template: GrogTemplateDef) -> None:
    """Undo what grog_templates.apply does only for a grog (Loyal +1 where
    the book's traits lack it), and note the companion in the Biography."""
    if not any(name == "Loyal" for name, _ in template.traits):
        character.personality_traits = [
            t
            for t in character.personality_traits
            if not (t.name == "Loyal" and t.score == 1)
        ]
    character.description.biography += (
        f"\n\nPlayed as a companion: a grog template becomes one by adding a "
        f"Story Flaw ({GROG_COMPANION_SOURCE})."
    )


def tally_line(
    template: ChoiceTemplateDef, chosen: Sequence[VirtueFlawInstance]
) -> str:
    """ "3 Virtue points, 3 Flaw points (of 10)"; a Mythic Companion's
    with the Virtue points its Flaws allow."""
    character = _blank(template.type)
    character.virtues_flaws = list(chosen)
    t = cv.tally(character)
    if template.type == "mythic companion":
        _, most = cv.virtue_allowance(character, t.flaw_points)
        return (
            f"{_points(t.virtue_points, 'Virtue')} of {most} allowed, "
            f"{_points(t.flaw_points, 'Flaw')} (of {cv.max_flaw_points(character)})"
        )
    return (
        f"{_points(t.virtue_points, 'Virtue')}, {_points(t.flaw_points, 'Flaw')} "
        f"(of {cv.max_flaw_points(character)})"
    )


# -- using a template --


def apply(
    saga: Saga,
    character: Character,
    template: ChoiceTemplateDef,
    choices: Choices,
) -> None:
    """Give `character` the Virtues and Flaws `choices` make of
    `template`, and the book's minimum Abilities as worksheet xp if they
    are wanted, leaving it In Creation for the worksheet to finish."""
    character.virtues_flaws = []
    for vf in chosen(template, choices):
        character.virtues_flaws.append(vf)
        cch.apply_virtue(saga, character, vf)
    if template.age:
        character.background.year_born = saga.current_year - template.age
    if choices.characteristics and template.characteristics:
        character.characteristics = replace(
            character.characteristics, **template.characteristics
        )
    character.personality_traits = [ScoredTrait(n, s) for n, s in template.traits]
    character.reputations = [ScoredTrait(n, s) for n, s in template.reputations]
    if choices.abilities and template.abilities:
        rows = ability_rows(template, choices.blanks)
        gt.spend(character, rows, native_name(template, choices.blanks))
        for entry, (name, _) in zip(template.abilities, rows, strict=True):
            ability = next((a for a in character.abilities if a.name == name), None)
            if ability is not None and entry.get("specialty"):
                ability.specialty = entry["specialty"]
    character.description.biography = biography(template, choices)
    character.in_creation = True


def where(template: ChoiceTemplateDef) -> str:
    """ "Definitive Edition, page 47"."""
    book = BOOK_NAMES.get(template.book) or sourcebooks.SOURCEBOOKS.get(
        template.book, template.book
    )
    return f"{book}, page {template.page}"


def biography(template: ChoiceTemplateDef, choices: Choices) -> str:
    """What the sheet's Biography starts as: the template it was built
    from and where it differs from the book."""
    version = variants(template)[choices.variant].get("name", "")
    head = f"Built from {template.name}" + (f", {version}" if version else "")
    parts = [f"{head} ({where(template)}). {template.concept}"]
    if template.notes:
        parts.append(f"Notes: {template.notes}")
    if template.fixes:
        parts.append(f"Where this differs from the book: {' '.join(template.fixes)}")
    return "\n\n".join(parts)


def flaw_words(template: ChoiceTemplateDef) -> str:
    """ "a Major Personality or Story Flaw"."""
    tier = template.flaw.get("tier", "Major")
    kinds = " or ".join(template.flaw.get("categories", ()))
    return f"a {tier} {kinds} Flaw"


def summary(template: ChoiceTemplateDef) -> str:
    """The New Character form's description of a template (markup)."""
    lines = [
        f"[b]{escape(template.name)}[/] ({escape(where(template))})",
        escape(template.concept),
    ]
    if template.flaw:
        lines.append(escape(f"With it: {flaw_words(template)}."))
    if template.kind == "sample":
        by_id = catalog.load_virtue_flaw_catalog_by_id()
        statuses = " or ".join(by_id[s].name for s in template.statuses if s in by_id)
        lines.append(escape(f"Age {template.age}; {statuses}."))
    elif template.abilities:
        lines.append(escape(f"Minimum Abilities: {abilities_text(template)}."))
    if template.notes:
        lines.append(f"[dim]{escape(template.notes)}[/]")
    return "\n".join(lines)
