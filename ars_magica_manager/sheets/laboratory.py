"""What a laboratory's page shows, independent of how it is drawn: who
works there and its aura, the eight Characteristics with where each comes
from, its Virtues and Flaws as cards, every Lab Total, its Specializations,
Features, rooms and stores, and its seasons.

Plain values rather than markup where a graphical page gives each its own
type; the longer passages (a Virtue's rules, the Base Lab Total) are the
same markup the terminal sheet shows, from laboratories.py and
lab_planning.py.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import catalog
from .. import laboratories as labs
from ..arts import FORMS, TECHNIQUES
from ..markup import escape
from ..models import LAB_CHARACTERISTICS, Character, Laboratory, Saga
from ..references import Fact
from ..rules import effects, lab_items, lab_stats, realms, sites
from ..rules import lab as lab_rules
from ..rules.realms import covenant_effective_aura


def owner(saga: Saga, lab: Laboratory) -> Character | None:
    return saga.character(lab.owner_id)


def sanctum(saga: Saga, magus: Character) -> Laboratory | None:
    """The magus's own laboratory, if they have one."""
    return saga.laboratory(magus.assigned_lab_id)


def subtitle(saga: Saga, lab: Laboratory) -> str:
    """The line under the name: whose it is, where and when."""
    magus = owner(saga, lab)
    covenant = saga.covenant(lab.covenant_id)
    parts = [f"The sanctum of {magus.name}" if magus else "No one's sanctum"]
    if covenant:
        parts.append(covenant.name)
    if lab.location:
        parts.append(lab.location)
    parts.append(f"{saga.current_season} {saga.current_year}")
    return "  ·  ".join(parts)


@dataclass(frozen=True)
class Aura:
    """The lab's aura: the covenant's (with any Boons), the lab's own
    modifier, the total, its realm and how it touches Hermetic magic."""

    covenant: int
    modifier: int
    total: int
    realm: str
    note: str
    #: Where the modifier comes from, for a tooltip.
    modifier_from: str = "here"


def aura(saga: Saga, lab: Laboratory) -> Aura:
    covenant = saga.covenant(lab.covenant_id)
    inherited = (
        covenant_effective_aura(
            covenant, catalog.load_covenant_boon_hook_catalog_by_id()
        )
        if covenant
        else 0
    )
    realm = covenant.aura_realm if covenant else "Magic"
    own = sites.lab_aura(saga, lab)
    if own is not None:
        inherited, realm = own
    total = lab_stats.lab_aura_total(lab, inherited)
    return Aura(
        inherited, lab.aura_modifier, total, realm, realms.aura_note(realm, total)
    )


@dataclass(frozen=True)
class Characteristic:
    """One Laboratory Characteristic: the typed part, what its Virtues and
    Flaws add, and the total."""

    key: str
    name: str
    manual: int
    virtues: int
    flaws: int
    #: Each Virtue or Flaw's part: "Servant +2 (Kurt's Intelligence +3,
    #: halved, rounded up)", "Superior Construction +1".
    sources: tuple[str, ...] = ()

    @property
    def total(self) -> int:
        return self.manual + self.virtues + self.flaws


def characteristics(lab: Laboratory, saga: Saga | None = None) -> list[Characteristic]:
    """The eight Characteristics; given the `saga`, a Servant who is one of
    its grogs counts with the grog's Intelligence."""
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    rows = []
    for key in LAB_CHARACTERISTICS:
        manual, virtues, flaws, _total = lab_stats.lab_characteristic_total(
            lab, by_id, key, saga
        )
        sources = tuple(
            _source_text(saga, effect)
            for effect in lab_stats.characteristic_effects(lab, by_id, key, saga)
        )
        rows.append(
            Characteristic(
                key, key.replace("_", " ").title(), manual, virtues, flaws, sources
            )
        )
    return rows


def _source_text(saga: Saga | None, effect: effects.Effect) -> str:
    """One Virtue or Flaw's part in a Characteristic: "Superior
    Construction +1", or for one read from an Intelligence, whose:
    "Servant +2 (Kurt's Intelligence +3, halved, rounded up)"."""
    text = f"{effect.entry.name} {effect.amount or 0:+g}"
    if effect.modifier.amount_param is None:
        return text
    return f"{text} ({labs.reading_detail(saga, effect.instance, effect.modifier)})"


def characteristic_text(row: Characteristic) -> str:
    """A Characteristic's working, for a details panel (app markup)."""
    return "\n".join(
        [
            f"[$label]Typed:[/] {row.manual:+d}",
            f"[$label]Virtues:[/] {row.virtues:+d}",
            f"[$label]Flaws:[/] {row.flaws:+d}",
            *(f"  {escape(source)}" for source in row.sources),
            "",
            f"[b]{escape(row.name)} {row.total:+d}[/]",
        ]
    )


def capacity_facts(lab: Laboratory) -> list[Fact]:
    """What the lab's Size leaves room for: the Size its Virtues and Flaws
    occupy, the points still free and the Safety that leaves."""
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    return [
        Fact("Occupied Size", f"{lab_stats.lab_occupied_size(lab, by_id):g}"),
        Fact("Free Virtues", f"{lab_stats.lab_free_virtues(lab, by_id):g}"),
        Fact("Base Safety", f"{lab_stats.lab_base_safety(lab, by_id):+g}"),
    ]


@dataclass(frozen=True)
class VirtueFlawCard:
    index: int  # into lab.virtues_flaws
    name: str
    tier: str  # "Free", "Minor", "Major"
    category: str
    summary: str  # its effects on Characteristics and Specializations


def virtue_flaw_cards(
    lab: Laboratory, side: str, saga: Saga | None = None
) -> list[VirtueFlawCard]:
    """The lab's Virtues or Flaws (`side`), each with what it does in
    a few words: "Safety +1, Aesthetics +1" (a Servant's Safety read from
    its grog's Intelligence, given the `saga`)."""
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    cards = []
    for index, instance in enumerate(lab.virtues_flaws):
        definition = by_id.get(instance.vf_id)
        if definition is None or definition.type != side:
            continue
        effects = labs.characteristic_effect_texts(instance, definition, saga)
        grants = labs.specialization_grant_text(instance, definition)
        if grants:
            effects.append(grants)
        cards.append(
            VirtueFlawCard(
                index,
                catalog.describe_virtue_flaw(instance, by_id),
                definition.tier,
                definition.category,
                ", ".join(effects),
            )
        )
    return cards


def lab_totals(
    saga: Saga, lab: Laboratory
) -> dict[tuple[str, str], lab_rules.LabTotal] | None:
    """The owner's Lab Total for every Technique and Form here, or None
    when no magus works here."""
    magus = owner(saga, lab)
    if magus is None or magus.type != "magus":
        return None
    return {
        (technique, form): lab_rules.lab_total(saga, magus, technique, form, lab)
        for technique in TECHNIQUES
        for form in FORMS
    }


def lab_total_text(total: lab_rules.LabTotal) -> str:
    """One Lab Total's terms (app markup)."""
    lines = []
    for line in total.lines:
        if line.amount is not None:
            lines.append(f"[$label]{escape(line.label)}[/] {line.amount:+g}")
        elif line.multiplier is not None:
            lines.append(f"[$label]{escape(line.label)}[/] x{line.multiplier:g}")
    lines += ["", f"[b]Lab Total {int(total.total)}[/]"]
    for note in total.notes or ():
        lines.append(f"[$text-warning]{escape(note)}[/]")
    return "\n".join(lines)


@dataclass(frozen=True)
class Specialization:
    name: str
    points: int
    counts: bool
    kind: str  # "Activity" or "Art"


def specializations(saga: Saga, lab: Laboratory) -> list[Specialization]:
    """Every Specialization the lab has points in, Activities first."""
    arts = (*TECHNIQUES, *FORMS)
    rows = [
        Specialization(
            s.name, s.points, s.counts, "Art" if s.name in arts else "Activity"
        )
        for s in lab_stats.specialization_scores(saga, lab)
        if s.points
    ]
    return sorted(rows, key=lambda s: (s.kind != "Activity", -s.points))


def specialization_text(saga: Saga, lab: Laboratory, name: str) -> str:
    """Where a Specialization's points come from (app markup)."""
    score = next(
        s for s in lab_stats.specialization_scores(saga, lab) if s.name == name
    )
    lines = [
        f"[$label]{escape(source)}[/] {points:+d}" for source, points in score.sources
    ]
    state = "counts" if score.counts else "doesn't count"
    if score.dropped:
        state = "turned off"
    return "\n".join([*lines, "", f"[b]{escape(name)} {score.points:+d}[/] ({state})"])


@dataclass(frozen=True)
class FeatureCard:
    index: int
    name: str
    kind: str  # "Cauldron, Lesser, Focus"
    problem: str  # the first thing still to do, or ""


def feature_cards(lab: Laboratory) -> list[FeatureCard]:
    cards = []
    for index, feature in enumerate(lab.features):
        virtue = labs.feature_virtue(lab, feature)
        details = [labs.feature_type_name(feature)]
        if virtue is not None:
            details.append(labs.tier_word(virtue.vf_id))
        if feature.focus:
            details.append("Focus")
        problems = labs.feature_problems(lab, feature)
        cards.append(
            FeatureCard(
                index, feature.name, ", ".join(details), problems[0] if problems else ""
            )
        )
    return cards


@dataclass(frozen=True)
class ItemCard:
    """One magic item effect, as the desktop's card shows it."""

    index: int
    name: str  # "Rowan Lectern: Steady Page"
    gives: str  # "Texts +2" or the Virtue it grants
    problem: str  # the first thing wrong, or ""


def item_cards(saga: Saga, lab: Laboratory) -> list[ItemCard]:
    cards = []
    for index, benefit in enumerate(lab.item_benefits):
        problems = lab_items.problems(saga, lab, benefit)
        gives = labs.item_gives(lab, benefit)
        cards.append(
            ItemCard(
                index,
                labs.item_name(saga, benefit),
                f"Grants {gives}" if benefit.granted_id else gives,
                problems[0] if problems else "",
            )
        )
    return cards
