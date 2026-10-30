"""A saga's own Mystery Cults, without a front-end: who belongs to one,
what each degree's Initiation needs, a Script's components and bonus, and
an experiment to find a degree's first Script.

Rules (The Mysteries Revised Edition, TMRE; the Definitive Edition, DE,
agrees on every figure it gives and wins where they differ):

- A cult has its own (Mystery Cult) Lore, which the storyguide creates;
  its founders may start with it at 0 (TMRE pp. 18-19). Membership is the
  Lore: one is inducted by gaining it, and its Virtues, most of which can
  also be taken at creation, only say which degree a member has reached
  (TMRE pp. 11, 13, 19). An Initiate needs the Lore at 1; the second and
  later Initiations typically need 3, a guideline the troupe may set
  aside (TMRE pp. 11, 13; DE p. 387).
- Each degree teaches a Mystery Virtue (TMRE p. 13). Initiation Total =
  the Mystagogue's Presence + Lore + the Script's bonus, no die, against
  15 for a Minor Virtue he knows, 21 for a Major, 18 and 30 when he lacks
  it (DE pp. 387-388; TMRE pp. 13-14).
- A Script's bonus is the sum of its components (TMRE pp. 15-16; DE p.
  388): a special place and time +3 (once), a Quest +3 (a unique one +6),
  a Minor Ordeal +3, a Medium +6, a Major +9, a Minor Virtue the Major one
  replaces +3, goods +1 (once), a season's service +1 (once), something of
  great value +3 to +6, the Mystagogue's time +3, and the rite's sympathy
  -5 to +5. A component that costs the Initiate nothing voids the whole
  Script (TMRE p. 16).
- With no Script, or only one that can't reach the Target for this
  Mystagogue, she experiments (TMRE p. 18): the rite's proposed bonus and
  a risk of 0 to +3; a stress die + risk on the Extraordinary Results
  chart; a simple die + risk + Intelligence + Lore against 9 + the bonus
  (15 + it on another Initiate); then the storyguide's sympathy joins the
  Script and the Initiation Total adds the risk, which the Script written
  down doesn't keep. The Target takes the Initiate's past-Ordeal
  reduction, never below 9 (TMRE p. 14). The rite's Ordeal Flaws are
  suffered even when it fails; a Disaster gives the Mystagogue and the
  Initiate a Major Flaw each. A Script that works keeps what the chart
  gave: a side effect or minor flaw or benefit as a Personality Trait, a
  major flaw as an extra Ordeal Flaw with no bonus, a major benefit as a
  Virtue, and a modified effect as the different Virtue it Initiates
  (TMRE p. 18; DE p. 388).
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field

from . import catalog, world
from .models import (
    Case,
    Character,
    Covenant,
    CultComponent,
    CultDegree,
    CultScript,
    MysteryCult,
    Ordeal,
    Saga,
    ScoredTrait,
    VirtueFlawDef,
    VirtueFlawInstance,
)
from .models.mystery_cults import (
    COMPONENT_KINDS,
    FLAW_KINDS,
    SAGA_CULT_PREFIX,
)
from .rules import dice, mysteries
from .rules.breakdown import Breakdown, Line
from .rules.scores import ability_level
from .rules.season_work.initiation import ordeal_reduction

SOURCE = (
    "The Mysteries Revised Edition pp. 13-19 (Inventing Your Own Cult pp. "
    "18-19); Ars Magica Definitive Edition pp. 387-389"
)
TMRE = "TMRE"

#: The components a cult's Script may hold: the Initiation season's own
#: table (rules.mysteries), the Minor Virtue a Major one replaces (TMRE p.
#: 15) and an experiment's proposed rite, until its components are
#: written out.
VIRTUE_REPLACED = mysteries.Component(
    "A Minor Virtue the Major one replaces", 3, once=True, key="virtue_replaced"
)
RITE = mysteries.Component(
    "The rite as proposed", 0, once=True, key="rite", least=0, most=40
)
#: An extra Ordeal Flaw an experiment's major flaw writes into the Script,
#: with no bonus (TMRE p. 18).
FLAWED_ORDEAL = mysteries.Component(
    "An experiment's Ordeal Flaw", 0, key="flawed_ordeal"
)
COMPONENTS: tuple[mysteries.Component, ...] = (
    *mysteries.COMPONENTS,
    VIRTUE_REPLACED,
    RITE,
    FLAWED_ORDEAL,
)
BY_KEY: dict[str, mysteries.Component] = {c.key: c for c in COMPONENTS}
assert set(BY_KEY) == set(COMPONENT_KINDS)

#: What each kind of component asks of the Initiate, for its details.
KIND_NOTES: dict[str, str] = {
    "place": "Travelling far to a special place at a special time; one bonus only.",
    "quest": "Any time before the Initiation; it counts for this Initiation only.",
    "unique_quest": "One no similar Quester could repeat (the head of the Minotaur).",
    "ordeal_minor": "Suffered during the Initiation; lowers the next three "
    "Targets by 3, 2, 1.",
    "ordeal_medium": "A Minor Flaw raised to a related Major one; lowers the "
    "next three Targets by 6, 4, 2.",
    "ordeal_major": "Suffered during the Initiation; lowers the next three "
    "Targets by 9, 6, 3.",
    "virtue_replaced": "The Minor Virtue the Major one requires and replaces: "
    "an Ordeal losing it.",
    "goods": "Material goods or wealth, a real loss; one bonus only.",
    "time": "A season serving another in the cult; one bonus only.",
    "great_sacrifice": "Something of great and symbolic value: a talisman, a "
    "familiar, a powerful device.",
    "mystagogue_time": "The Mystagogue's time, such as a season teaching.",
    "sympathy": "How fitting the rite is to the Virtue, agreed with the "
    "storyguide (usually 0 to +3).",
    "rite": "The experiment's rite as a whole: write its components out with "
    "Edit Script.",
    "flawed_ordeal": "An Ordeal Flaw the experiment's major flaw added: it "
    "gives no bonus.",
}

NUMERALS = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII")


def numeral(index: int) -> str:
    """A degree's numeral, by its place (0 for the first)."""
    return NUMERALS[index] if index < len(NUMERALS) else str(index + 1)


# -- ids and lookups ---------------------------------------------------------


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "cult"


def new_cult_id(saga: Saga, name: str) -> str:
    base = SAGA_CULT_PREFIX + _slug(name)
    taken = {c.id for c in saga.custom_cults}
    ident, n = base, 2
    while ident in taken:
        ident, n = f"{base}_{n}", n + 1
    return ident


def new_degree_id(cult: MysteryCult) -> str:
    taken = {d.id for d in cult.degrees}
    n = len(cult.degrees) + 1
    while f"degree_{n}" in taken:
        n += 1
    return f"degree_{n}"


def virtue_of(degree: CultDegree) -> VirtueFlawDef | None:
    return catalog.load_virtue_flaw_catalog_by_id().get(degree.virtue_id)


def tier_of(degree: CultDegree) -> str:
    """The tier of the degree's Virtue, Minor when it isn't known."""
    virtue = virtue_of(degree)
    return virtue.tier if virtue is not None and virtue.tier == "Major" else "Minor"


def virtue_name(degree: CultDegree) -> str:
    virtue = virtue_of(degree)
    if virtue is None:
        return "(no Virtue)" if not degree.virtue_id else f"{degree.virtue_id} (gone)"
    return catalog.describe_virtue_flaw(initiated(degree), {degree.virtue_id: virtue})


def initiated(degree: CultDegree) -> VirtueFlawInstance:
    """The Virtue the degree gives, with what it names."""
    return VirtueFlawInstance(degree.virtue_id, dict(degree.virtue_params))


def mystery_virtues() -> list[VirtueFlawDef]:
    """The Virtues a degree may teach: every Minor or Major Virtue, the
    saga's own included, by name. (Almost any Virtue may be Initiated, save
    those of birth or circumstance, TMRE p. 13: the troupe's choice.)"""
    return sorted(
        (
            v
            for v in catalog.load_virtue_flaw_catalog()
            if v.side == "Virtue" and v.tier in ("Minor", "Major")
        ),
        key=lambda v: (v.name, v.tier),
    )


def ordeal_flaws() -> list[VirtueFlawDef]:
    """The Flaws an Ordeal may inflict: every Minor or Major Flaw, by name
    (Hermetic Flaws too, TMRE p. 13)."""
    return sorted(
        (
            v
            for v in catalog.load_virtue_flaw_catalog()
            if v.side == "Flaw" and v.tier in ("Minor", "Major")
        ),
        key=lambda v: (v.name, v.tier),
    )


def founder_name(saga: Saga, cult: MysteryCult) -> str:
    founder = saga.character(cult.founder_id)
    return founder.name if founder is not None else ""


def lore_score(character: Character, cult: MysteryCult) -> int:
    return ability_level(character, cult.lore) if cult.lore else 0


def holds_lore(character: Character, cult: MysteryCult) -> bool:
    return bool(cult.lore) and any(a.name == cult.lore for a in character.abilities)


def holds(character: Character, degree: CultDegree) -> bool:
    """Whether `character` has the degree's Virtue (naming the same thing,
    when the degree's names one)."""
    return bool(degree.virtue_id) and any(
        vf.vf_id == degree.virtue_id
        and (not degree.virtue_params or vf.params == degree.virtue_params)
        for vf in character.virtues_flaws
    )


# -- members -----------------------------------------------------------------


@dataclass(frozen=True)
class Member:
    """A member of the cult: the highest degree whose Virtue he holds
    (None for a probationer, who has only the Lore)."""

    character: Character
    degree: int | None


def is_member(character: Character, cult: MysteryCult) -> bool:
    """Whether `character` belongs to the cult: he holds its Lore, at any
    score, or is its founder, who may have it at 0 (TMRE pp. 11, 13, 19).
    One of its Virtues alone doesn't make a member: most can be taken at
    creation."""
    return holds_lore(character, cult) or (
        bool(cult.founder_id) and character.id == cult.founder_id
    )


def members(saga: Saga, cult: MysteryCult) -> list[Member]:
    """Who belongs to the cult (worked out, not listed): those holding its
    Lore, and its founder, each at the highest degree whose Virtue he
    holds, highest degree first."""
    found = []
    for character in saga.characters:
        if not is_member(character, cult):
            continue
        held = [i for i, d in enumerate(cult.degrees) if holds(character, d)]
        found.append(Member(character, max(held) if held else None))
    found.sort(
        key=lambda m: (-(m.degree if m.degree is not None else -1), m.character.name)
    )
    return found


def members_text(saga: Saga, cult: MysteryCult) -> str:
    """ "Hildegund (III), Matthaios (I), 2 probationers"."""
    found = members(saga, cult)
    if not found:
        return "none yet"
    named = [
        f"{m.character.name} ({numeral(m.degree)})"
        for m in found
        if m.degree is not None
    ]
    probationers = sum(1 for m in found if m.degree is None)
    if probationers:
        named.append(f"{probationers} probationer{'s' if probationers != 1 else ''}")
    return ", ".join(named)


def holders(saga: Saga, degree: CultDegree) -> list[Character]:
    """The saga's characters holding the degree's Virtue: Mystagogues who
    know it."""
    return [c for c in saga.characters if holds(c, degree)]


def mystagogues(saga: Saga, cult: MysteryCult) -> list[Character]:
    """Who may lead the cult's Initiations: its members with the Lore at 1
    or more, best Presence + Lore first."""
    found = [
        m.character for m in members(saga, cult) if lore_score(m.character, cult) >= 1
    ]
    return sorted(
        found, key=lambda c: -(_characteristic(c, cult) + lore_score(c, cult))
    )


def _characteristic(character: Character, cult: MysteryCult) -> int:
    return int(getattr(character.characteristics, cult.characteristic.lower(), 0))


# -- Targets and totals ----------------------------------------------------


def degree_target(saga: Saga, degree: CultDegree) -> int:
    """The Target of the degree's Initiation for the cult's best-placed
    Mystagogue: known when someone holds its Virtue (15 / 21), else new
    (18 / 30), before any past Ordeal."""
    known = bool(holders(saga, degree))
    return mysteries.TARGET_LEVELS[tier_of(degree), known]


def initiation_total(
    mystagogue: Character, cult: MysteryCult, bonus: int, risk: int = 0
) -> Breakdown:
    """The Mystagogue's Characteristic + the cult's Lore + the Script's
    bonus (+ an experiment's risk). No die."""
    lines = [
        Line(
            cult.characteristic, amount=_characteristic(mystagogue, cult), source=SOURCE
        ),
        Line(cult.lore or "Lore", amount=lore_score(mystagogue, cult), source=SOURCE),
        Line("Script", amount=bonus, source=SOURCE),
    ]
    if risk:
        lines.append(Line("Risk", amount=risk, source=mysteries.EXPERIMENT_SOURCE))
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def target_for(
    mystagogue: Character, degree: CultDegree, initiate: Character | None = None
) -> int:
    """The Target for this Mystagogue: 15 / 21 when he holds the Virtue,
    else 18 / 30, less the Initiate's past-Ordeal reduction, never below
    9 (TMRE p. 14)."""
    base = mysteries.TARGET_LEVELS[tier_of(degree), holds(mystagogue, degree)]
    if initiate is None:
        return base
    return max(mysteries.MINIMUM_TARGET, base - ordeal_reduction(initiate))


def script_inadequate(
    cult: MysteryCult,
    degree: CultDegree,
    mystagogue: Character,
    initiate: Character | None = None,
) -> bool:
    """Whether the degree's Script won't do for this Mystagogue, so she may
    experiment (TMRE p. 18): there is none, it Initiates a different
    Virtue, or her Initiation Total with it falls short of the Target."""
    script = degree.script
    if script is None or script.initiates:
        return True
    total = initiation_total(mystagogue, cult, script.bonus).total
    return total < target_for(mystagogue, degree, initiate)


# -- Scripts -----------------------------------------------------------------


def component_bonus(key: str, size: int = 0) -> int:
    """What a component of kind `key` adds: the troupe's size for one it
    sizes (a great sacrifice, the sympathy, an experiment's rite), else the
    table's bonus."""
    component = BY_KEY[key]
    return size if component.sized else component.bonus


def component(
    key: str, size: int = 0, note: str = "", flaw_id: str = ""
) -> CultComponent:
    return CultComponent(key, component_bonus(key, size), note.strip(), flaw_id)


def script_problem(components: list[CultComponent]) -> str:
    """What makes a Script's components invalid ("" if nothing): a
    once-only kind twice, a size outside its range, or an Ordeal (or an
    experiment's Ordeal Flaw) without its Flaw (TMRE pp. 15-16, 18)."""
    for part in components:
        kind = BY_KEY.get(part.key)
        if kind is None:
            return f"{part.key!r} isn't a kind of Script component."
        if kind.once and sum(c.key == part.key for c in components) > 1:
            return f"A Script may hold {COMPONENT_KINDS[part.key].lower()} only once."
        if kind.sized:
            assert kind.least is not None and kind.most is not None
            if not kind.least <= part.bonus <= kind.most:
                return (
                    f"{COMPONENT_KINDS[part.key]} is {kind.least:+d} to "
                    f"{kind.most:+d}, not {part.bonus:+d}."
                )
        if part.key in FLAW_KINDS and not part.flaw_id:
            return "Choose the Flaw each Ordeal inflicts."
    return ""


def component_name(part: CultComponent) -> str:
    """How a component's row names it: what it is, or for an Ordeal its
    Flaw, else its kind (an experiment's rite with its Ordeal's Flaw)."""
    flaw = catalog.load_virtue_flaw_catalog_by_id().get(part.flaw_id)
    flaw_text = f"{flaw.name} ({flaw.tier} Flaw)" if flaw is not None else "a Flaw"
    if part.key in FLAW_KINDS:
        return f"Ordeal: {flaw_text}" + (f", {part.note}" if part.note else "")
    named = part.note or COMPONENT_KINDS[part.key]
    return f"{named}; Ordeal: {flaw_text}" if part.flaw_id else named


def bonus_words(script: CultScript) -> str:
    """ "special place +3, Quest +3, Minor Ordeal +3 = +9"."""
    parts = [f"{COMPONENT_KINDS[c.key]} {c.bonus:+d}" for c in script.components]
    return (", ".join(parts) or "nothing") + f" = {script.bonus:+d}"


def count_of(script: CultScript | None, key: str) -> int:
    return sum(1 for c in script.components if c.key == key) if script else 0


def first_of(script: CultScript | None, keys: tuple[str, ...]) -> CultComponent | None:
    if script is None:
        return None
    return next((c for c in script.components if c.key in keys), None)


def reconcile(
    old: list[CultComponent], wanted: dict[str, list[CultComponent]]
) -> list[CultComponent]:
    """A Script's components after its form: for each kind in `wanted`,
    the old ones of that kind are kept (their words too) as far as the new
    count goes, each given the new one's bonus and Flaw, and any more are
    added at the end; kinds the form doesn't set are kept as they were."""
    kept: list[CultComponent] = []
    used: dict[str, int] = {}
    for part in old:
        if part.key not in wanted:
            kept.append(part)
            continue
        n = used.get(part.key, 0)
        if n < len(wanted[part.key]):
            new = wanted[part.key][n]
            kept.append(
                CultComponent(part.key, new.bonus, part.note or new.note, new.flaw_id)
            )
            used[part.key] = n + 1
    for key, parts in wanted.items():
        kept += parts[used.get(key, 0) :]
    return kept


# -- changes -------------------------------------------------------------------


def changed(saga: Saga) -> None:
    """After any change to the saga's cults: the catalogs take it up."""
    catalog.use_saga(saga)


def rename_lore(saga: Saga, old: str, new: str) -> None:
    """A cult's Lore renamed: every character holding it keeps it under
    the new name."""
    if not old or old == new:
        return
    for character in saga.characters:
        for ability in character.abilities:
            if ability.name == old:
                ability.name = new


def lore_problem(saga: Saga, cult: MysteryCult | None, lore: str) -> str:
    """Why a cult's Lore can't be named `lore` ("" if it can): blank, or
    another cult's, or an Ability of the catalog's own."""
    lore = lore.strip()
    if not lore:
        return "Name the cult's Lore."
    if any(c.lore == lore for c in saga.custom_cults if c is not cult):
        return f"Another of the saga's cults has {lore} as its Lore."
    own = {f"{c.id}_lore" for c in saga.custom_cults}
    if any(a.name == lore and a.id not in own for a in catalog.load_ability_catalog()):
        return f"{lore} is an Ability of the catalog: give the cult its own Lore."
    return ""


# -- experimenting ---------------------------------------------------------------


@dataclass
class Experiment:
    """An experiment's first two rolls (TMRE p. 18): what the
    Extraordinary Results chart made of the rite, and its validity."""

    notes: list[str] = field(default_factory=list)
    #: Whether the rite can still give the Virtue (a fatal flaw, a
    #: complete failure or Disaster, or an invalid rite, end it).
    goes_on: bool = True
    #: Whether the risk still counts in the Initiation Total.
    risk_counts: bool = True
    #: What the chart writes into the Script if the rite works: its side
    #: effects (each a Personality Trait), how many extra Ordeal Flaws and
    #: Virtues, and whether a different Virtue is Initiated.
    traits: list[str] = field(default_factory=list)
    major_flaws: int = 0
    major_benefits: int = 0
    modified: bool = False
    #: A Disaster: a Major Flaw for the Mystagogue and the Initiate.
    disaster: bool = False


@dataclass
class Findings:
    """What the troupe makes of the chart's results, and the Flaw of the
    rite's own Ordeal (TMRE p. 18): the Personality Traits ("Devoted to
    the cult +1"), the extra Ordeal Flaws and Virtues (catalog ids), and
    the Virtue a modified effect Initiates instead ("" for the degree's)."""

    rite_flaw: str = ""
    traits: list[str] = field(default_factory=list)
    flaws: list[str] = field(default_factory=list)
    virtues: list[str] = field(default_factory=list)
    instead: str = ""


_TRAIT = re.compile(r"^(?P<name>.*?\S)\s+(?P<score>[+-]\d+)$")


def parse_trait(text: str) -> ScoredTrait | None:
    """ "Devoted to the cult +1" as a Personality Trait (None if it has no
    signed score at its end)."""
    found = _TRAIT.match(text.strip())
    if found is None:
        return None
    return ScoredTrait(found["name"], int(found["score"]))


def experiment(
    rng: random.Random,
    saga: Saga,
    cult: MysteryCult,
    mystagogue: Character,
    on_self: bool,
    proposed: int,
    risk: int,
) -> Experiment:
    """The chart, then the validity: a simple die + risk + Intelligence +
    Lore against 9 + the proposed bonus, or 15 + it on another."""
    rite = mysteries.experimental_rite(rng, risk, saga)
    found = Experiment(
        notes=list(rite.notes),
        risk_counts=rite.risk_counts,
        traits=list(rite.traits),
        major_flaws=rite.major_flaws,
        major_benefits=rite.major_benefits,
        modified=rite.modified,
        disaster=rite.disaster,
    )
    ease = mysteries.validity_ease(proposed, on_self)
    die = dice.simple_die(rng)
    valid = (
        die
        + risk
        + mystagogue.characteristics.intelligence
        + lore_score(mystagogue, cult)
    )
    found.notes.append(
        f"The rite's validity: die {die} + risk {risk} + Intelligence "
        f"{mystagogue.characteristics.intelligence} + Lore "
        f"{lore_score(mystagogue, cult)} = {valid} against {ease}: "
        + ("valid." if valid >= ease else "invalid, so no Virtue is gained.")
    )
    found.goes_on = not rite.no_virtue and valid >= ease
    return found


def written_script(
    degree: CultDegree, proposed: int, sympathy: int, found: Findings | None = None
) -> CultScript:
    """The Script an experiment that worked writes down: the rite as
    proposed (with its Ordeal's Flaw) and the storyguide's sympathy,
    without the risk, and what the chart wrote into it: its Personality
    Traits, its extra Ordeal Flaws (no bonus), its extra Virtues and the
    different Virtue a modified effect Initiates (TMRE p. 18)."""
    found = found or Findings()
    parts = [
        component(
            "rite",
            proposed,
            "the components the Mystagogue proposed",
            found.rite_flaw,
        )
    ]
    if sympathy:
        parts.append(component("sympathy", sympathy))
    parts += [component("flawed_ordeal", flaw_id=flaw) for flaw in found.flaws]
    return CultScript(
        f"The first rite of the {degree.name}",
        parts,
        traits=[t.strip() for t in found.traits if t.strip()],
        virtues=list(found.virtues),
        initiates=found.instead,
    )


def vf_name(vf_id: str) -> str:
    known = catalog.load_virtue_flaw_catalog_by_id().get(vf_id)
    return known.name if known is not None else vf_id


def _gain(character: Character, vf_id: str) -> bool:
    """Give `character` a Virtue or Flaw he lacks; whether he gained it."""
    if not vf_id or any(
        vf.vf_id == vf_id and not vf.params for vf in character.virtues_flaws
    ):
        return False
    character.virtues_flaws.append(VirtueFlawInstance(vf_id))
    return True


def suffer_ordeals(initiate: Character, flaws: list[str], initiated: bool) -> list[str]:
    """The rite's Ordeal Flaws, suffered whether it worked or not (TMRE
    p. 18): each Flaw the Initiate lacks is added, and the largest is
    kept as his Ordeal, to lower his next Initiations' Targets. One that
    gave its Virtue uses up a step of each past Ordeal's reduction, as an
    Initiation season does."""
    if initiated:
        for ordeal in initiate.ordeals:
            ordeal.initiations_since += 1
        initiate.ordeals = [o for o in initiate.ordeals if o.initiations_since < 3]
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    gained = [f for f in flaws if _gain(initiate, f)]
    tiers = {by_id[f].tier for f in flaws if f in by_id}
    if tiers & {"Minor", "Major"}:
        initiate.ordeals.append(Ordeal("Major" if "Major" in tiers else "Minor"))
    if not gained:
        return []
    names = ", ".join(vf_name(f) for f in gained)
    return [f"{initiate.name} suffers the Ordeal: {names}."]


def disaster(
    saga: Saga,
    mystagogue: Character,
    initiate: Character,
    mystagogue_flaw: str,
    initiate_flaw: str,
    rite_flaw: str = "",
) -> list[str]:
    """A Disaster on the chart: the Initiation fails completely, and the
    Mystagogue and the Initiate each gain a Major Flaw (TMRE p. 18); the
    rite's own Ordeal is still suffered."""
    notes = suffer_ordeals(initiate, [rite_flaw] if rite_flaw else [], False)
    for person, flaw in ((mystagogue, mystagogue_flaw), (initiate, initiate_flaw)):
        if _gain(person, flaw):
            notes.append(f"{person.name} gains the Major Flaw {vf_name(flaw)}.")
    changed(saga)
    return notes


def finish_experiment(
    saga: Saga,
    cult: MysteryCult,
    degree: CultDegree,
    mystagogue: Character,
    initiate: Character,
    proposed: int,
    sympathy: int,
    risk: int,
    found: Findings | None = None,
) -> list[str]:
    """The third step: the Initiation Total with the sympathy and the risk
    against the Mystagogue's Target (less the Initiate's past-Ordeal
    reduction). When it is met the Initiate gains the Virtue (or the one a
    modified effect Initiates instead) and what the chart added, and the
    degree its Script. The rite's Ordeal Flaws are suffered either way
    (TMRE p. 18)."""
    found = found or Findings()
    total = initiation_total(mystagogue, cult, proposed + sympathy, risk).total
    target = target_for(mystagogue, degree, initiate)
    said = (
        f"Initiation Total {total} ({cult.characteristic} + {cult.lore} + Script "
        f"{proposed + sympathy:+d} + risk {risk}) against {target}: "
    )
    flaws = [f for f in (found.rite_flaw, *found.flaws) if f]
    if total < target:
        notes = [
            said + "the rite fails. Its Quests and Ordeals are spent; they can't "
            "count in a later attempt (TMRE p. 19)."
        ]
        notes += suffer_ordeals(initiate, flaws, False)
        changed(saga)
        return notes
    old = degree.script
    degree.script = written_script(degree, proposed, sympathy, found)
    notes = [
        said + "the rite works, and its Script is written down (the risk isn't "
        "kept in it, TMRE p. 18)."
        + (f" It replaces {old.name}." if old is not None else "")
    ]
    if found.instead:
        if _gain(initiate, found.instead):
            notes.append(
                f"{initiate.name} gains {vf_name(found.instead)}, not the "
                "degree's own Virtue: the effect was modified."
            )
    elif not holds(initiate, degree) and degree.virtue_id:
        initiate.virtues_flaws.append(initiated(degree))
        notes.append(f"{initiate.name} gains {virtue_name(degree)}.")
    for extra in found.virtues:
        if _gain(initiate, extra):
            notes.append(f"{initiate.name} also gains {vf_name(extra)}.")
    for text in degree.script.traits:
        trait = parse_trait(text)
        if trait is not None and all(
            t.name.lower() != trait.name.lower() for t in initiate.personality_traits
        ):
            initiate.personality_traits.append(trait)
            notes.append(f"{initiate.name} gains the Personality Trait {text}.")
    notes += suffer_ordeals(initiate, flaws, True)
    notes.append("The season itself is the Initiate's to plan.")
    changed(saga)
    return notes


def experiments_for(saga: Saga, character: Character) -> list[tuple[int, int]]:
    """The cults `character` may experiment in as Mystagogue, each as (its
    row, the row of its first degree open to an experiment): one with no
    Script, or one whose Script won't do for a Mystagogue (TMRE p. 18)."""
    found = []
    for row, cult in enumerate(saga.custom_cults):
        if character not in mystagogues(saga, cult):
            continue
        degree = next(
            (d for d in range(len(cult.degrees)) if offers_experiment(saga, row, d)),
            None,
        )
        if degree is not None:
            found.append((row, degree))
    return found


def offers_experiment(saga: Saga, cult_row: int | None, degree_row: int | None) -> bool:
    """Whether Experiment on a Script can act on the degree at `degree_row`
    of the cult at `cult_row` (the first cult when none is chosen): one with
    no Script yet, or one whose Script won't do for one of its Mystagogues
    (TMRE p. 18)."""
    cults = saga.custom_cults
    if not cults:
        return False
    cult = (
        cults[cult_row]
        if cult_row is not None and 0 <= cult_row < len(cults)
        else cults[0]
    )
    if degree_row is None or not 0 <= degree_row < len(cult.degrees):
        return False
    degree = cult.degrees[degree_row]
    return degree.script is None or any(
        script_inadequate(cult, degree, guide) for guide in mystagogues(saga, cult)
    )


# -- as factions (secret societies in the Order's politics) --------------------


def cults_of(saga: Saga, covenant: Covenant) -> set[str]:
    """The saga cults any of the covenant's magi belongs to, by name."""
    people = [c for c in saga.characters if c.covenant_id == covenant.id]
    return {
        cult.name
        for cult in saga.custom_cults
        for person in people
        if is_member(person, cult)
    }


def cult_leaning(saga: Saga, case: Case, covenant: Covenant) -> tuple[str, str] | None:
    """How a covenant leans on `case` for its magi's cult: with a covenant
    sharing a cult that is a party, else by the cult's attitude toward a
    troupe covenant that is a party (Warm or better with it, Wary or worse
    against it). Which side ("brought_by" or "against") and why; None when
    no cult of its magi takes a side. A cult's members voting as one is
    the app's reading, as the Rhine's gilds are."""
    own = cults_of(saga, covenant)
    if not own:
        return None
    for other in saga.covenants:
        if other is covenant:
            continue
        shared = own & cults_of(saga, other)
        name = other.name.strip().casefold()
        if not shared or not name:
            continue
        cult = min(shared)
        if name in case.brought_by.casefold():
            return "brought_by", f"its cult, {cult}, stands with {other.name}"
        if name in case.against.casefold():
            return "against", f"its cult, {cult}, stands with {other.name}"
    for cult in saga.custom_cults:
        if cult.name not in own:
            continue
        for attitude in cult.attitudes:
            troupe = saga.covenant(attitude.covenant_id)
            score = world.attitude_score(attitude)
            if troupe is None or not score or not troupe.name.strip():
                continue
            name = troupe.name.strip().casefold()
            side = (
                "brought_by"
                if name in case.brought_by.casefold()
                else "against"
                if name in case.against.casefold()
                else ""
            )
            if not side:
                continue
            if score < 0:
                side = "against" if side == "brought_by" else "brought_by"
            word = world.attitude_word(score)
            return (
                side,
                f"its cult, {cult.name}, is {word.lower()} toward {troupe.name}",
            )
    return None
