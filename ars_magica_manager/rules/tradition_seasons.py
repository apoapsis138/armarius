"""A hedge tradition's seasons: Opening a student's Gift to it, the
Initiation Total of its scripts, and each tradition's own work.

Opening The Gift (Hedge Magic RE, Introduction): a season that occupies
master and student. Both need The Gift, and the master must already be
Opened to the tradition.

    Opening Ease Factor = 2 x the student's Supernatural Ability and Art
                          scores (+ 12 if his Gift was already Opened)
    Opening Total       = the tradition's OpeningRule (most use a Lab
                          Total: a Characteristic + Abilities + aura)

- A student with no such scores is Opened whatever the total.
- Below the Ease Factor the Opening fails; up to twice it, the student is
  Opened but loses his old Supernatural Abilities and Arts (and their
  Virtues and Flaws); above twice it he keeps them.
- An Ability or Art from a Minor Virtue counts as at least 2, from a
  Major one at least 6.
- For each of the tradition's Opening Arts the master has below 2, the
  student gains a Flaw: the tradition's (a vitki's Minor Magical
  Deficiency for that rune), or one the troupe picks.

Initiation Total = the Mystagogue's Characteristic (Presence) + the
tradition's Lore + the Script's bonus, against the Script's Ease Factor,
+ 3 (Minor) or + 9 (Major) when the Mystagogue doesn't know the power
(Hedge Magic Revised Edition p. 13). The undergo_initiation season
(rules/supplement_work) carries it out when the plan names the Script,
with the unGifted rules of p. 14 (rules/mysteries).

A tradition's own seasons (TraditionDef.activities) give Exposure in
the Art or Ability worked, and name the Lab Total of the work.

Rules: Opening The Gift; each Hedge Magic tradition's Opening,
initiations and laboratory work.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .. import catalog, sourcebooks
from ..models import (
    SUPERNATURAL_CATEGORIES,
    Character,
    GroupCasting,
    InitiationScript,
    OpeningRule,
    Saga,
    SeasonPlan,
    TraditionActivity,
    TraditionDef,
    VirtueFlawInstance,
)
from ..models.mystery_cults import is_saga_cult
from . import hedge_casting as hc
from . import realms, tradition_totals
from .breakdown import Breakdown, Line
from .creation_access import ability_def, ability_xp_table, traditions_of
from .creation_tradition import opened_ability
from .warping import opened_to_arts

SOURCE = (
    "Hedge Magic, Revised Edition, Chapter One: Introduction, Opening The Gift, pp. 7-8"
)

OPEN = "open_tradition_gift"
#: How far a master must reach for each outcome.
FAILS, LOSES, KEEPS, AUTOMATIC = "fails", "loses", "keeps", "automatic"
ALREADY_OPENED = 12
COMPETENT = 2
MINOR_FLOOR, MAJOR_FLOOR = 2, 6


def openable(character: Character) -> list[TraditionDef]:
    """The traditions the character can Open a student to: those with an
    Opening the character, Gifted, has been Opened to."""
    if not hc.gifted(character):
        return []
    return [
        t
        for t in traditions_of(character)
        if t.opening is not None
        and all(hc.holds(character, a) for a in t.training.opening)
    ]


def opening_total(
    master: Character,
    tradition: TraditionDef,
    aura: int = 0,
    aura_realm: str = realms.HERMETIC,
) -> Breakdown:
    """The master's Opening Total, with its terms."""
    rule = tradition.opening
    assert rule is not None
    lines: list[Line] = []
    value = getattr(master.characteristics, rule.characteristic.lower(), 0)
    lines.append(Line(rule.characteristic, amount=value, source=SOURCE))
    for name in rule.adds:
        lines.append(Line(name, amount=hc.score(master, name), source=SOURCE))
    if rule.highest_of:
        best = max(rule.highest_of, key=lambda n: hc.score(master, n))
        lines.append(
            Line(f"{best} (highest)", amount=hc.score(master, best), source=SOURCE)
        )
    if rule.lowest_of:
        low = min(rule.lowest_of, key=lambda n: hc.score(master, n))
        lines.append(
            Line(f"{low} (lowest)", amount=hc.score(master, low), source=SOURCE)
        )
    if rule.aura:
        lines.append(
            Line(
                f"Aura ({aura_realm} {aura})",
                amount=hc.aura_modifier(tradition, aura, aura_realm),
                source=realms.SOURCE,
            )
        )
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def _virtue_tiers(character: Character) -> dict[str, str]:
    """The tier of each Virtue the character has, by its name (a
    Supernatural Ability's Virtue shares its name)."""
    by_id = {e.id: e for e in catalog.load_virtue_flaw_catalog()}
    tiers: dict[str, str] = {}
    for vf in character.virtues_flaws:
        entry = by_id.get(vf.vf_id)
        if entry is not None and entry.type == "Virtue":
            tiers[entry.name] = entry.tier
    return tiers


def supernatural_scores(character: Character) -> list[tuple[str, int]]:
    """Each Supernatural Ability and hedge Art the character has, with the
    score the Opening counts (at least 2 from a Minor Virtue, 6 from a
    Major one), and each Hermetic Art he has opened (xp above 0): the
    Opening Ease Factor counts every Art score (Hedge Magic RE p. 8)."""
    tiers = _virtue_tiers(character)
    found = []
    for ability in character.abilities:
        entry = ability_def(ability.name)
        category = entry.category if entry is not None else ability.category
        if category not in SUPERNATURAL_CATEGORIES:
            continue
        floor = {"Minor": MINOR_FLOOR, "Major": MAJOR_FLOOR}.get(
            tiers.get(ability.name, ""), 0
        )
        found.append((ability.name, max(hc.score(character, ability.name), floor)))
    for art, value in character.arts.items():
        if value.xp > 0:
            found.append((art, value.level))
    return found


def already_opened(character: Character, tradition: TraditionDef) -> bool:
    """Whether the student's Gift was Opened before: to another
    tradition, or his Hermetic Arts (a magus, or any Art with xp, as
    warping.opened_to_arts counts them)."""
    if opened_to_arts(character):
        return True
    return any(
        t.id != tradition.id and t.opening is not None for t in openable(character)
    )


def sabbat_group(tradition: TraditionDef, total: str) -> GroupCasting | None:
    """The tradition's gathering that helps with `total` (the folk
    witches' sabbat: "Opening Total", "Initiation Total", "Brew Potency")."""
    return next((g for g in tradition.groups if total in g.applies_to), None)


def _group_name(tradition: TraditionDef, total: str) -> str:
    group = sabbat_group(tradition, total)
    return group.name if group is not None else "gathering"


def sabbat_bonus(
    tradition: TraditionDef, total: str, helpers: int, aura: int, aura_realm: str
) -> int:
    """What `helpers` witches assisting at a sabbat add to `total`: +1
    each, up to the Magic aura's strength at the site (Hedge Magic RE
    pp. 45-46); 0 for a tradition with no such gathering."""
    group = sabbat_group(tradition, total)
    if group is None or helpers <= 0:
        return 0
    return hc.group_bonus(group, [0] * helpers, aura=aura, aura_realm=aura_realm)


def opening_ease(student: Character, tradition: TraditionDef) -> int:
    total = 2 * sum(value for _, value in supernatural_scores(student))
    if already_opened(student, tradition):
        total += ALREADY_OPENED
    return total


def opening_result(total: int, ease: int, rule: OpeningRule | None = None) -> str:
    """Whether an Opening fails, Opens losing the student's Supernatural
    Abilities, or Opens keeping them: at least the Ease Factor Opens, more
    than twice it keeps (Hedge Magic Revised Edition p. 8), unless the
    tradition sets its own bands (the Amazons: twice, and four times or
    more, Rival Magic p. 30)."""
    rule = rule or OpeningRule()
    if ease <= 0:
        return AUTOMATIC
    if total < rule.opens_at * ease:
        return FAILS
    if rule.keeps_at is not None:
        return KEEPS if total >= rule.keeps_at * ease else LOSES
    return KEEPS if total > rule.keeps_over * ease else LOSES


@dataclass
class TraditionWork:
    """What a season of a tradition's work does: an Opening's outcome, or
    the Lab Total of the tradition's own work."""

    tradition_id: str
    total: int = 0
    ease: int = 0
    result: str = ""
    #: An Opening's Arts the master has below 2.
    flawed: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def opens(self) -> bool:
        return self.result in (AUTOMATIC, LOSES, KEEPS)


def open_work(
    saga: Saga, master: Character, plan: SeasonPlan
) -> tuple[list[str], TraditionWork | None]:
    """Opening a student's Gift to the master's tradition (the first he
    can Open to)."""
    traditions = openable(master)
    if not traditions:
        return [
            f"{master.name} must have The Gift and be Opened to a tradition "
            "that Opens its students."
        ], None
    tradition = traditions[0]
    student = saga.character(plan.subject_id)
    if student is None or student is master:
        return ["Choose the student."], None
    if not hc.gifted(student):
        return [f"{student.name} doesn't have The Gift."], None
    if tradition.id in student.traditions and not [
        a for a in tradition.training.opening if not hc.holds(student, a)
    ]:
        return [f"{student.name} is already Opened to {tradition.name}."], None
    aura, realm = realms.home_aura(saga, master)
    total = int(opening_total(master, tradition, aura, realm).total)
    gathering = plan.other_modifier and sabbat_group(tradition, "Opening Total")
    if gathering and plan.site_aura is None:
        return [
            "Enter the Magic aura at the sabbat's site: it caps the witches "
            "who may help (Hedge Magic RE pp. 45-46)."
        ], None
    helped = sabbat_bonus(
        tradition,
        "Opening Total",
        plan.other_modifier,
        plan.site_aura or 0,
        realms.HERMETIC,
    )
    total += helped
    ease = opening_ease(student, tradition)
    work = TraditionWork(
        tradition.id,
        total=total,
        ease=ease,
        result=opening_result(total, ease, tradition.opening),
    )
    work.flawed = [
        a for a in tradition.training.opening if hc.score(master, a) < COMPETENT
    ]
    work.notes.append(_opening_note(student, tradition, work))
    if plan.other_modifier and sabbat_group(tradition, "Opening Total") is not None:
        work.notes.append(
            f"{helped:+d} from {plan.other_modifier} helpers at the "
            f"{_group_name(tradition, 'Opening Total')} (at most the Magic aura "
            f"at its site, {plan.site_aura}, count)."
        )
    return [], work


def _opening_note(
    student: Character, tradition: TraditionDef, work: TraditionWork
) -> str:
    if work.result == AUTOMATIC:
        said = f"{student.name} has no Supernatural Abilities or Arts: Opened to {tradition.name}."
    else:
        said = (
            f"Opening Total {work.total} against {work.ease}: "
            + {
                FAILS: "the Opening fails.",
                LOSES: (
                    f"Opened to {tradition.name}, but {student.name} loses the "
                    "Supernatural Abilities and Arts he had, and their Virtues and "
                    "Flaws (remove them by hand)."
                ),
                KEEPS: f"Opened to {tradition.name}, keeping what he had.",
            }[work.result]
        )
    rule = tradition.opening
    if work.opens and rule is not None and rule.loses_other_arts:
        said += " The Arts of any other tradition are lost (remove them by hand)."

    if work.opens and work.flawed:
        rule = tradition.opening
        assert rule is not None
        names = ", ".join(work.flawed)
        if rule.flaw:
            said += f" A flawed Opening: a Flaw for each of {names}."
        else:
            said += (
                f" A flawed Opening (the master is below {COMPETENT} in "
                f"{names}): a Flaw for each, the troupe's choice."
            )
    return said


def apply_opening(student: Character, work: TraditionWork) -> None:
    """The student joins the tradition with its Opening's Arts at 0, the
    Virtues it gives, and the Flaws of a flawed Opening."""
    if not work.opens:
        return
    tradition = catalog.load_tradition_catalog_by_id()[work.tradition_id]
    if tradition.id not in student.traditions:
        student.traditions.append(tradition.id)
    held = {a.name for a in student.abilities}
    for name in tradition.training.opening:
        if name not in held:
            student.abilities.append(opened_ability(name))
    have = {vf.vf_id for vf in student.virtues_flaws}
    for vf_id in tradition.training.opening_virtues:
        if vf_id not in have:
            student.virtues_flaws.append(VirtueFlawInstance(vf_id))
    rule = tradition.opening
    if rule is not None and rule.flaw:
        for name in work.flawed:
            params = {rule.flaw_param: name} if rule.flaw_param else {}
            student.virtues_flaws.append(VirtueFlawInstance(rule.flaw, params=params))


# ---------------------------------------------------------------------------
# Initiation


def initiation_total(mystagogue: Character, tradition: TraditionDef, bonus: int) -> int:
    """Presence + the tradition's Lore + the Script's bonus. An
    Organization Lore with no organization named counts the best one."""
    rule = tradition.initiation
    assert rule is not None
    value = getattr(mystagogue.characteristics, rule.characteristic.lower(), 0)
    return value + lore_score(mystagogue, rule.lore) + bonus


#: Hermetic Mystery Cults whose members are known by a Virtue, not by
#: naming the tradition: House Verditius's, by its Outer Mystery (Houses of
#: Hermes: Mystery Cults p. 117).
VIRTUE_MEMBERS: dict[str, str] = {
    "trad_verditius_mysteries": "vf_verditius_magic",
    # House Merinita's, by Faerie Magic (Houses of Hermes: Mystery Cults p. 85).
    "trad_merinita_mysteries": "vf_faerie_magic",
    # House Bjornaer's, by the Heartbeast (Houses of Hermes: Mystery Cults p. 18).
    "trad_bjornaer_mysteries": "vf_heartbeast",
    # House Criamon's, by the Enigma (DE p. 235).
    "trad_criamon_mysteries": "vf_the_enigma",
}


def belongs(character: Character, tradition_id: str) -> bool:
    """Whether `character` is one of the tradition: named on the sheet, or
    holding the Virtue that makes him one (VIRTUE_MEMBERS), or for a
    saga's own cult, holding its Lore (saga_cult_member)."""
    virtue = VIRTUE_MEMBERS.get(tradition_id)
    return (
        tradition_id in character.traditions
        or (
            virtue is not None
            and any(vf.vf_id == virtue for vf in character.virtues_flaws)
        )
        or saga_cult_member(character, tradition_id)
    )


def saga_cult_member(character: Character, tradition_id: str) -> bool:
    """Whether `character` belongs to a saga's own Mystery Cult: he holds
    its Lore, at any score (one is inducted by gaining it; a probationer
    has it at 1, and a founder may at 0). Its Virtues alone don't make a
    member, since most can be taken at creation (The Mysteries Revised
    Edition pp. 11, 13, 19)."""
    if not is_saga_cult(tradition_id):
        return False
    tradition = catalog.load_tradition_catalog_by_id().get(tradition_id)
    if tradition is None:
        return False
    lores = set(tradition.abilities)
    return any(a.name in lores for a in character.abilities)


def _saga_cults() -> list[str]:
    """The ids of the saga in use's own Mystery Cults."""
    return [t.id for t in catalog.load_tradition_catalog() if is_saga_cult(t.id)]


def script_key(tradition: TraditionDef, script: InitiationScript) -> str:
    """How a season plan names a hedge Script (SeasonPlan.hedge_script)."""
    return f"{tradition.id}/{script.name}"


def hedge_script(key: str) -> tuple[TraditionDef, InitiationScript] | None:
    """The tradition and Script a plan's `hedge_script` names (None for
    none, or one no longer in the catalog)."""
    tradition_id, _, name = key.partition("/")
    tradition = catalog.load_tradition_catalog_by_id().get(tradition_id)
    if tradition is None or tradition.initiation is None:
        return None
    script = next((s for s in tradition.initiation.scripts if s.name == name), None)
    return (tradition, script) if script is not None else None


def script_options(saga: Saga, initiate: Character) -> list[tuple[str, str]]:
    """The hedge Scripts an Initiation season may follow: those of the
    traditions the Initiate or anyone in the saga belongs to (the
    Mystagogue must be one of them), save the Forest Paths' kind, which
    has no Initiation Total, and a saga cult whose source is out of play."""
    cults = _saga_cults()
    held = {
        tradition_id
        for person in (initiate, *saga.characters)
        for tradition_id in (*person.traditions, *VIRTUE_MEMBERS, *cults)
        if belongs(person, tradition_id)
    }
    found: list[tuple[str, str]] = []
    for tradition in catalog.load_tradition_catalog():
        rule = tradition.initiation
        if tradition.id not in held or rule is None or rule.roll_less:
            continue
        if is_saga_cult(tradition.id) and sourcebooks.own_source_out(
            saga, tradition.source
        ):
            continue
        for script in rule.scripts:
            found.append(
                (
                    f"{tradition.name}: {script.name} (Ease {script.ease_factor}, "
                    f"+{script.bonus})",
                    script_key(tradition, script),
                )
            )
    return found


def hedge_lore(tradition: TraditionDef) -> str:
    """The Lore a tradition's Initiation Total uses, for the season's notes."""
    rule = tradition.initiation
    return (rule.lore if rule is not None else "") or "Lore"


def lore_score(character: Character, lore: str) -> int:
    if not lore:
        return 0
    if ":" in lore or any(a.name == lore for a in character.abilities):
        return hc.score(character, lore)
    lores = [a.name for a in character.abilities if a.name.startswith(lore + ":")]
    return max((hc.score(character, n) for n in lores), default=0)


# ---------------------------------------------------------------------------
# Each tradition's own seasons


def activity(key: str) -> tuple[TraditionDef, TraditionActivity] | None:
    for tradition in catalog.load_tradition_catalog():
        for found in tradition.activities:
            if found.key == key:
                return tradition, found
    return None


def lab_total(
    character: Character,
    tradition: TraditionDef,
    rule_name: str,
    subject: str,
    aura: int,
    realm: str,
) -> tuple[str, int] | None:
    """The best Lab Total of `rule_name` that uses `subject` (any, when
    none does): its label and total."""
    rule = next((r for r in tradition.casting if r.name == rule_name), None)
    if rule is None:
        return None
    found = hc.castings(character, tradition, rule)
    using = [c for c in found if subject in c.uses] or found
    if not using:
        return None
    best = max(
        using,
        key=lambda c: (
            hc.casting_score(
                character, tradition, rule, c.uses, aura=aura, aura_realm=realm
            ).total
        ),
    )
    total = hc.casting_score(
        character, tradition, rule, best.uses, aura=aura, aura_realm=realm
    ).total
    return best.label, int(total)


def work(
    saga: Saga, character: Character, plan: SeasonPlan, subject: str
) -> tuple[list[str], TraditionWork | None]:
    """A season of the tradition's own work, Exposure in `subject` (an
    Ability or Art name)."""
    found = activity(plan.activity)
    if found is None:
        return [f"Unknown activity {plan.activity!r}."], None
    tradition, chosen = found
    if tradition.id not in character.traditions:
        return [f"{character.name} isn't one of the {tradition.name}."], None
    if chosen.gifted_only and not hc.gifted(character):
        return [f"{chosen.label} needs The Gift."], None
    if subject and subject not in tradition.abilities:
        return [
            f"{chosen.label} gives Exposure in one of the {tradition.name}' "
            "Arts or Abilities."
        ], None
    result = TraditionWork(tradition.id)
    if chosen.lab_rule:
        aura, realm = realms.home_aura(saga, character)
        total = lab_total(character, tradition, chosen.lab_rule, subject, aura, realm)
        if total is not None:
            label, value = total
            result.total = value
            result.notes.append(f"{chosen.lab_rule} ({label}): {value}.")
            result.notes += tradition_totals.season_notes(
                saga, character, chosen.key, value
            )
    return [], result


def practice_forbidden(character: Character, name: str) -> TraditionDef | None:
    """The character's tradition whose Arts can't be practised, when
    `name` is one of them (a hedge Art)."""
    for tradition in traditions_of(character):
        if tradition.advancement.practice_arts or name not in tradition.abilities:
            continue
        entry = ability_def(name)
        if ability_xp_table(name) == "art" or (
            entry is not None and entry.category == "Hedge Art"
        ):
            return tradition
    return None
