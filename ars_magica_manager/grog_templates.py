"""Grog Templates: Grogs, Chapter 7's guidance for nineteen kinds of
grog (the Advisor, the Bull, the Confessor...), offered on New Character
for a grog while Grogs is in play. Unlike the Definitive Edition's
ready-made characters (character_templates.py), each is a set of choices:
a version of the template where the book gives several (the Confessor's
faith, the Craftsman's stage), an age and its Ability list, a Social
Status, the book's Virtues and Flaws and the ones it suggests, and
Personality Traits. The New Character form asks for them
(forms/grog_templates.py) before the template is used.

Using one keeps the character In Creation: its Abilities go on as
Creation Worksheet xp (the Native Language, a Virtue's own xp, the free
score of a Supernatural Ability, Early Childhood, then Later Life), so the
worksheet checks the book's list against the rules for its age. Its
Virtues and Flaws must keep to a grog's limits (Definitive Edition,
Chapter Three: no Major Virtues or Flaws, no Hermetic ones, at most three
Minor Flaws and no more Virtue points than Flaw points, one Social
Status); limit_problem() says what a choice breaks.

Rules: SOURCE; each entry's `fixes` say where it differs from the page.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from typing import Any

from . import catalog, creation, sourcebooks
from .markup import escape
from .models import (
    Character,
    CreationXp,
    GrogTemplateDef,
    Saga,
    ScoredTrait,
    VirtueFlawInstance,
)
from .rules import creation_access as access
from .rules import creation_characteristics as cch
from .rules import creation_finish as finish
from .rules import creation_later as later
from .rules import creation_virtues as cv
from .rules import creation_xp as cx
from .rules.xp import ability_xp

SOURCE = (
    "Grogs, Chapter 7: Grog Templates (https://www.redcap.org/page/"
    "Grogs_Chapter_Seven:_Grog_Templates)"
)
BOOK = "Grogs"


@dataclass(frozen=True)
class Variant:
    """One version of a template: its Social Statuses, the book's own
    Virtues and Flaws, its ages, the Abilities it renames ("Theology:
    Christian" to "Theology: Islam") and what to say about a Flaw the
    book gives that a grog can't take."""

    name: str
    statuses: tuple[str, ...]
    virtues_flaws: tuple[dict[str, Any], ...]
    ages: tuple[dict[str, Any], ...]
    renames: tuple[tuple[str, str], ...] = ()
    flaw_hint: str = ""


@dataclass
class Choices:
    """What the player chose from a template: indexes into variants() and
    the variant's ages, the Social Status (a vf_id), every other Virtue
    and Flaw, whether to take the book's Characteristics, and the
    Personality Traits."""

    variant: int = 0
    age: int = 0
    status: str = ""
    virtues_flaws: list[VirtueFlawInstance] = field(default_factory=list)
    characteristics: bool = False
    traits: list[tuple[str, int]] = field(default_factory=list)

    def all_virtues_flaws(self) -> list[VirtueFlawInstance]:
        status = [VirtueFlawInstance(self.status)] if self.status else []
        return status + list(self.virtues_flaws)


def in_play(saga: Saga | None) -> bool:
    return sourcebooks.in_play(BOOK, sourcebooks.saga_books(saga))


def templates(saga: Saga | None) -> list[GrogTemplateDef]:
    """The templates offered for a new grog: none while Grogs is out of
    play."""
    return catalog.load_grog_template_catalog() if in_play(saga) else []


def find(template_id: str | None) -> GrogTemplateDef | None:
    if not template_id:
        return None
    return catalog.load_grog_template_catalog_by_id().get(template_id)


def instance(entry: dict[str, Any]) -> VirtueFlawInstance:
    return VirtueFlawInstance(entry["vf_id"], dict(entry["params"]))


def variants(template: GrogTemplateDef) -> list[Variant]:
    """The template's versions, each with what it doesn't replace taken
    from the template; one, unnamed, when the book gives no versions."""
    found = template.variants or [{"name": ""}]
    return [
        Variant(
            name=v["name"],
            statuses=tuple(v.get("statuses") or template.statuses),
            virtues_flaws=tuple(v.get("virtues_flaws", template.virtues_flaws)),
            ages=tuple(v.get("ages") or template.ages),
            renames=tuple((v.get("renames") or {}).items()),
            flaw_hint=v.get("flaw_hint") or template.flaw_hint,
        )
        for v in found
    ]


def age_label(entry: dict[str, Any]) -> str:
    """ "Age 20", or "Age 15, Apprentice"."""
    label = entry.get("label")
    return f"Age {entry['age']}" + (f", {label}" if label else "")


def _rows(template: GrogTemplateDef, choices: Choices) -> list[dict[str, Any]]:
    variant = variants(template)[choices.variant]
    renames = dict(variant.renames)
    return [
        {**row, "name": renames.get(row["name"], row["name"])}
        for row in variant.ages[choices.age]["abilities"]
    ]


def _xp_rows(rows: Sequence[dict[str, Any]]) -> cx.XpRows:
    return tuple(
        (row["name"], ability_xp(row["score"]) + row.get("xp", 0)) for row in rows
    )


def blanks(template: GrogTemplateDef, choices: Choices) -> list[str]:
    """The names the chosen Ability list leaves to the player ("area",
    "covenant", "craft"), in the order it first asks for them."""
    return cx.template_blanks(_xp_rows(_rows(template, choices)))


def list_xp(template: GrogTemplateDef, choices: Choices) -> int:
    """The xp the chosen Ability list adds up to."""
    return sum(xp for _, xp in _xp_rows(_rows(template, choices)))


def age_xp(age: int) -> int:
    """A grog's starting xp at `age`: the Native Language and Early
    Childhood, then 15 a year."""
    childhood = cx.NATIVE_XP + cx.CHILDHOOD_XP
    years = max(0, age - later.CHILDHOOD_ENDS)
    return childhood + years * later.XP_A_YEAR


# -- the grog limits --


def limit_problem(chosen: Sequence[VirtueFlawInstance]) -> str | None:
    """Why a grog can't take `chosen` (the Definitive Edition's limits),
    or None if it can."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    grog = Character(id="", name="", type="grog", virtues_flaws=list(chosen))
    t = cv.tally(grog)
    entries = [by_id[vf.vf_id] for vf in chosen if vf.vf_id in by_id]
    hermetic = [
        e.name for e in entries if catalog.needs_the_gift(e) or e.id in catalog.GIFT_IDS
    ]
    if hermetic:
        return f"A grog can't take The Gift or Hermetic Virtues or Flaws: {', '.join(hermetic)}."
    majors = [e.name for e in entries if e.tier == "Major"]
    if majors:
        return f"A grog takes no Major Virtues or Flaws: {', '.join(majors)}."
    most = cv.max_minor_flaws(grog)
    if t.minor_flaws > most:
        return f"A grog takes at most {most} Minor Flaws: {t.minor_flaws} chosen."
    if t.virtue_points > t.flaw_points:
        return (
            f"{_points(t.virtue_points, 'Virtue')} but only "
            f"{_points(t.flaw_points, 'Flaw')}: take another Flaw or leave a "
            "Virtue out."
        )
    if len(t.social_statuses) != 1:
        return (
            "A grog has one Social Status: "
            + (", ".join(t.social_statuses) or "none")
            + " chosen."
        )
    if t.repeated:
        return f"Taken more often than the book allows: {', '.join(t.repeated)}."
    return None


def tally_line(chosen: Sequence[VirtueFlawInstance]) -> str:
    """ "3 Virtue points, 3 Flaw points (3 of 3 Minor Flaws)"."""
    grog = Character(id="", name="", type="grog", virtues_flaws=list(chosen))
    t = cv.tally(grog)
    return (
        f"{_points(t.virtue_points, 'Virtue')}, {_points(t.flaw_points, 'Flaw')} "
        f"({t.minor_flaws} of {cv.max_minor_flaws(grog)} Minor Flaws)"
    )


def _points(count: int, side: str) -> str:
    return f"{count} {side} point{'' if count == 1 else 's'}"


# -- using a template --


def apply(
    saga: Saga,
    character: Character,
    template: GrogTemplateDef,
    choices: Choices,
    values: dict[str, str] | None = None,
) -> None:
    """Fill `character` from `template` as `choices` say, leaving it In
    Creation. `values` fills the blanks (blanks()); a blank left out
    keeps its placeholder. The rules ask every grog for Loyal and every
    warrior for Brave: one the book's traits lack starts at +1."""
    values = values or {}
    c = character
    variant = variants(template)[choices.variant]
    entry = variant.ages[choices.age]
    c.background.year_born = saga.current_year - entry["age"]
    if choices.characteristics and template.characteristics:
        c.characteristics = replace(c.characteristics, **template.characteristics)
    c.virtues_flaws = []
    for vf in choices.all_virtues_flaws():
        c.virtues_flaws.append(vf)
        cch.apply_virtue(saga, c, vf)
    c.personality_traits = [ScoredTrait(n, s) for n, s in choices.traits]
    c.reputations = [ScoredTrait(n, s) for n, s in template.reputations]
    rows = _rows(template, choices)
    filled = cx.fill_template(_xp_rows(rows), values)
    native = cx.fill_template(((entry["native"], 0),), values)[0][0]
    spend(c, filled, native)
    for row, (name, _) in zip(rows, filled, strict=True):
        if row.get("specialty"):
            ability = next((a for a in c.abilities if a.name == name), None)
            if ability is not None:
                ability.specialty = row["specialty"]
    for trait, needed in (("Loyal", True), ("Brave", finish.warrior(c))):
        if needed and not finish.has_trait(c, trait):
            c.personality_traits.append(ScoredTrait(trait, 1))
    c.description.biography = biography(template, variant, choices)
    c.in_creation = True


def spend(character: Character, rows: Sequence[tuple[str, int]], native: str) -> None:
    """Put each Ability's xp on the Creation Worksheet, step by step: the
    Native Language's 75, the free score of a Supernatural Ability a
    Virtue grants, each Virtue's own xp on what it may buy, Early
    Childhood on what a child may learn, then Later Life for the rest
    (even past its budget, which the worksheet then shows)."""
    c = character
    left = {name: xp for name, xp in rows}
    order = [name for name, _ in rows]

    def put(step: str, name: str, budget: int | None, note: str = "") -> int:
        """Spend up to `budget` xp (None: all it needs) on `name`; the xp
        spent."""
        need = left.get(name, 0)
        if need <= 0 or budget == 0:
            return 0
        multiplier = access.xp_multiplier(c, name)
        xp = access.xp_giving(need, multiplier)
        if budget is not None:
            xp = min(xp, budget)
        entry = CreationXp(step, name, xp, note)
        creation.spend_creation_xp(c, entry)
        left[name] = need - creation.gained_xp(entry)
        return xp

    if native in left and not cx.feral(c):
        entry = CreationXp("childhood", native, cx.NATIVE_XP, cx.NATIVE)
        creation.spend_creation_xp(c, entry)
        left[native] -= creation.gained_xp(entry)
    for name in order:
        if name in later.free_score_abilities(c):
            put("free", name, later.FREE_SUPERNATURAL_XP)
    supernatural = {
        name for name in order if access.ability_category(name) == access.SUPERNATURAL
    }
    for vf_id, rule in access.virtue_xp(c).items():
        budget = rule.xp
        for name in order:
            if name not in supernatural and access.virtue_xp_allows(rule, name):
                budget -= put("virtue", name, budget, vf_id)
    budget = cx.childhood_xp(c)
    for name in order:
        if cx.childhood_allows(name, c):
            budget -= put("childhood", name, budget)
    for name in order:
        put("later_life", name, None)


def biography(template: GrogTemplateDef, variant: Variant, choices: Choices) -> str:
    """What the sheet's Biography starts as: the template it was built
    from, the book's details for Virtues and Flaws with no parameter to
    hold them, its notes, and where this version differs from the page."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    noted = [
        vf
        for vf in (*variant.virtues_flaws, *_pool_entries(template))
        if vf.get("note")
    ]
    taken = choices.all_virtues_flaws()
    details = [
        f"{catalog.describe_virtue_flaw(instance(vf), by_id)} ({vf['note']})"
        for vf in noted
        if instance(vf) in taken
    ]
    version = f", {variant.name}" if variant.name else ""
    age = variant.ages[choices.age]["age"]
    parts = [
        f"Built from {template.name}{version} at age {age} (Grogs, Chapter 7: "
        f"Grog Templates, page {template.page}). {template.concept}"
    ]
    if details:
        parts.append(f"Details: {'; '.join(details)}.")
    if template.characteristics_advice:
        parts.append(f"Characteristics: {template.characteristics_advice}")
    if template.packages:
        parts.append(f"Training packages: {template.packages}.")
    if template.notes:
        parts.append(f"Notes: {template.notes}")
    if template.fixes:
        parts.append(f"Where this differs from the book: {' '.join(template.fixes)}")
    return "\n\n".join(parts)


def _pool_entries(template: GrogTemplateDef) -> list[dict[str, Any]]:
    """Every entry the pool offers, a single pick's options each."""
    return [
        option for entry in template.pool for option in entry.get("one_of", [entry])
    ]


def summary(template: GrogTemplateDef) -> str:
    """The New Character form's description of a template (markup): its
    page, what it is, its ages and Social Status, and its notes."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    lines = [
        f"[b]{escape(template.name)}[/] (Grogs, page {template.page})",
        escape(template.concept),
    ]
    for variant in variants(template):
        ages = ", ".join(str(a["age"]) for a in variant.ages)
        statuses = " or ".join(by_id[s].name for s in variant.statuses if s in by_id)
        head = f"{variant.name}: " if variant.name else ""
        lines.append(escape(f"{head}ages {ages}; {statuses}"))
    if template.notes:
        lines.append(f"[dim]{escape(template.notes)}[/]")
    return "\n".join(lines)
