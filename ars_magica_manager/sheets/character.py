"""What the Character sheet shows, independent of how it is drawn.

Each function returns one section's text (in the app's markup, see
markup.py) or its rows, from the saga and the character; a front-end lays
them out. The terminal and desktop sheets both read these, so the two
cannot disagree about what a character's sheet says.
"""

from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass

from .. import casting_text as ct
from .. import catalog, experiment_text, faith, traditions, tribunal_packages
from .. import lab_texts as lt
from .. import players as pl
from .. import possessions as pos
from .. import sheet_text as st
from .. import spells as spl
from ..arts import ART_ABBREVIATIONS, ART_DESCRIPTIONS, FORMS, TECHNIQUES
from ..markup import aligned, escape, inherited, markdown_text, problem
from ..models import (
    ABILITY_CATEGORIES,
    FULL,
    LINE,
    Ability,
    ArtScore,
    Character,
    Saga,
    TraditionDef,
    VirtueFlawInstance,
    Wounds,
    character_age,
)
from ..references import Fact
from ..rules import (
    aging,
    casting,
    derived,
    experiment,
    medicine,
    penetration,
    scores,
    warping,
)
from ..rules import animal_grogs as ag
from ..rules import creation_virtues as cv
from ..rules import xp as xp_rules
from ..rules.breakdown import Breakdown
from ..rules.realms import home_aura
from ..tables import Table
from ..world import signed


def info_left_text(saga: Saga, character: Character) -> str:
    """The top panel's first column: setting, age and the saga's date."""
    b = character.background
    age = character_age(b.year_born, saga.current_year)
    return aligned(
        [
            ("Setting", b.setting or "(not set)"),
            ("Age", age if age is not None else "(unknown -- set Year Born)"),
            ("Current Year", inherited(escape(str(saga.current_year)))),
            ("Current Season", inherited(escape(saga.current_season))),
        ]
    )


def info_right_text(saga: Saga, character: Character) -> str:
    """The top panel's second column: covenant, lab, type, Confidence,
    Faith and Size."""
    covenant = saga.covenant(character.covenant_id)
    place = tribunal_packages.place_word(saga, covenant).title()
    rows = [(place, escape(covenant.name) if covenant else "(unassigned)")]
    rows += [
        (label, escape(value))
        for label, value in tribunal_packages.magus_facts(saga, character)
    ]
    if character.detail != FULL:
        rows.append(("Detail", character.detail))
    if character.type == "magus":
        lab = saga.laboratory(character.assigned_lab_id)
        rows.append(
            ("Assigned Laboratory", escape(lab.name) if lab else "(unassigned)")
        )
    b = character.background
    rows += [("Type", character.type)]
    rows += [(label, escape(value)) for label, value in animal_facts(character)]
    rows += [
        ("Confidence Score", str(b.confidence_score)),
        ("Confidence Points", str(b.confidence_points)),
    ]
    if faith.shows_faith(character):
        rows += [
            ("True Faith Score", st.faith_score_text(character, saga)),
            ("Faith Points", str(b.faith_points)),
        ]
    elif resistance := penetration.faith_magic_resistance(character, saga):
        rows.append(("Magic Resistance", f"{resistance} (the Dominion)"))
    rows.append(("Size", st.size_text(character)))
    return aligned(rows)


def animal_facts(character: Character) -> list[tuple[str, str]]:
    """An animal grog's kind, its Presence and Communication with humans,
    and any human Language its Cunning reads down (plain text); none for
    a person."""
    if character.animal is None:
        return []
    found = [
        ("Animal", ag.describe(character.animal)),
        ("With humans", ag.penalties_text(character, short=True)),
    ]
    understood = [
        f"{a.name.split(': ', 1)[-1]} {a.level} as "
        f"{ag.understood(character, a.name, a.level)}"
        for a in character.abilities
        if ag.understood(character, a.name, a.level) != a.level
    ]
    if understood:
        found.append(("Understands", ", ".join(understood)))
    return found


def biographical_left_text(saga: Saga, character: Character) -> str:
    """Biographical Detail's first column: every Background and Description
    field but the Biography (the setting, Confidence and Size are in the
    top panel)."""
    b, d = character.background, character.description
    played_by = []
    if saga.players:  # a hosted saga's sign-in
        player = pl.player_by_id(saga, b.player_id)
        played_by = [f"Played by: {escape(player.name) if player else '(no one)'}"]
    return "\n".join(
        [
            f"Player: {escape(b.player) or '(not set)'}",
            *played_by,
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
            f"Physical Description: {markdown_text(d.physical_description) or '(not set)'}",
        ]
    )


def biographical_right_text(character: Character) -> str:
    """Biographical Detail's second column: the free-text Biography."""
    return markdown_text(character.description.biography) or "(none recorded)"


def aging_text(character: Character, saga: Saga | None = None) -> str:
    """Aging & Warping: Decrepitude, the aging roll's figures (a
    physician's regimen among them) and Warping."""
    a = character.aging
    lines = [f"Decrepitude: {a.decrepitude}"]
    # The yearly aging roll's figures, once there are any.
    if a.decrepitude_points:
        lines[0] += f" ({a.decrepitude_points} points)"
    if a.apparent_age is not None:
        lines.append(f"Apparent age: {a.apparent_age}")
    points = [f"{n.title()} {p}" for n, p in a.aging_points.items() if p]
    if points:
        lines.append("Aging Points: " + ", ".join(points))
    if a.longevity_modifier:
        lines.append(f"Longevity Ritual: -{a.longevity_modifier} to aging rolls")
        lines += experiment_text.effect_lines(
            a.longevity_effects, "The ritual's experimental effects"
        )
    if a.regimen and saga is not None:
        lines.append(
            medicine.regimen_text(
                saga.character(a.regimen_by),
                a.regimen,
                a.regimen_since,
                saga.current_year,
            )
        )
    if a.recovering:
        lines.append(f"Recovering from an Aging Crisis: {a.recovering}")
    return "\n".join(
        [
            *lines,
            "Effects of Aging:",
            markdown_text(a.effects) or "(none recorded)",
            "",
            f"Warping: {a.warping_score}/{a.warping_points}",
        ]
    )


def raw_vis_rows(character: Character) -> list[tuple[int | None, str]]:
    """One row per Art the character holds vis of, by Art name."""
    return [
        (index, f"{art.title()}: {character.raw_vis[art]} pawn(s)")
        for index, art in enumerate(sorted(character.raw_vis))
    ]


def raw_vis_table(pool: Mapping[str, int]) -> Table:
    """Raw Vis by Art name, as raw_vis_rows orders it (plain cells)."""
    return Table(
        ["Art", "Pawns"], [[art.title(), str(pool[art])] for art in sorted(pool)]
    )


def house_name(character: Character) -> str | None:
    """The magus's House by name, or None if it isn't set."""
    house_id = character.hermetic.house
    house = catalog.load_house_catalog_by_id().get(house_id) if house_id else None
    return house.name if house else None


def hermetic_background_left_text(character: Character) -> str:
    """Hermetic Background's first column: everything but the Wizard's
    Sigil."""
    h = character.hermetic
    house = house_name(character)
    apprenticed = h.age_of_apprenticeship
    return "\n".join(
        [
            f"House: {escape(house) if house else '(not set)'}",
            f"Domus Magna: {escape(h.domus_magna) or '(not set)'}",
            f"Primus: {escape(h.primus) or '(not set)'}",
            f"Parens: {escape(h.parens) or '(not set)'}",
            f"Covenant of Apprenticeship: "
            f"{escape(h.covenant_of_apprenticeship) or '(not set)'}",
            f"Age of Apprenticeship: "
            f"{apprenticed if apprenticed is not None else '(not set)'}",
        ]
    )


def hermetic_background_right_text(saga: Saga, character: Character) -> str:
    """Hermetic Background's second column: the Wizard's Sigil, and whose
    raw Lab Texts the magus reads."""
    sigil = character.hermetic.wizards_sigil
    return (
        f"Wizard's Sigil: {escape(sigil) or '(not set)'}\n"
        f"{lt.access_text(saga, character)}"
    )


def _fraction(xp: int, level_xp: int, next_xp: int) -> float:
    """How far `xp` has come from the current score's total to the next's."""
    return (xp - level_xp) / max(next_xp - level_xp, 1)


@dataclass(frozen=True)
class ArtRow:
    """One Art's line on the sheet: its score as shown (with any bonus, as
    "10 (13)"), its experience, and the totals the score began at
    (`level_xp`) and the next score needs (`next_xp`)."""

    art: str
    abbreviation: str
    score: str
    xp: int
    level_xp: int = 0
    next_xp: int = 1

    @property
    def fraction(self) -> float:
        """The way to the next score, from 0 to 1."""
        return _fraction(self.xp, self.level_xp, self.next_xp)


def art_row(character: Character, art: str) -> ArtRow:
    score = character.arts.get(art.lower(), ArtScore())
    bonus, _ = scores.art_bonus(character.virtues_flaws, art)
    progress = score.progress
    return ArtRow(
        art,
        ART_ABBREVIATIONS[art],
        st.adjusted_score(score.level, bonus),
        score.xp,
        xp_rules.xp_for_score(progress.score, xp_rules.ART_FACTOR),
        progress.next_total,
    )


def art_rows(character: Character, arts: Sequence[str]) -> list[ArtRow]:
    return [art_row(character, art) for art in arts]


@dataclass(frozen=True)
class AbilityRow:
    """One Ability as a table row: `index` into the character's Abilities,
    its score as shown (with any bonus) and its experience, as ArtRow."""

    index: int
    category: str
    name: str
    specialty: str
    score: str
    xp: int
    level_xp: int
    next_xp: int

    @property
    def fraction(self) -> float:
        return _fraction(self.xp, self.level_xp, self.next_xp)


def ability_table(character: Character) -> list[AbilityRow]:
    """The character's Abilities, grouped by category in the book's order
    (ABILITY_CATEGORIES), each kept in the order it was added."""
    return abilities_table(character.abilities, character.virtues_flaws)


def abilities_chapter_table(character: Character) -> list[AbilityRow]:
    """The Abilities chapter: ability_table without the Abilities a
    tradition's own chapter shows."""
    claimed = traditions.claimed(character)
    return [row for row in ability_table(character) if row.name not in claimed]


def tradition_table(character: Character, tradition: TraditionDef) -> list[AbilityRow]:
    """A tradition's chapter: the character's Arts and Abilities of that
    tradition, as ability_table rows whose category is the heading they
    sit under (Techniques, Forms, Runes, Abilities...)."""
    return [
        _ability_row(character.virtues_flaws, index, heading, ability)
        for heading, group in traditions.chapter_groups(character, tradition)
        for index, ability in group
    ]


def _ability_row(
    virtues_flaws: Sequence[VirtueFlawInstance],
    index: int,
    category: str,
    ability: Ability,
) -> AbilityRow:
    bonus, _ = scores.ability_bonus(virtues_flaws, ability.name)
    progress = ability.progress
    return AbilityRow(
        index,
        category,
        ability.name,
        ability.specialty or "",
        st.adjusted_score(progress.score, bonus),
        progress.total,
        xp_rules.xp_for_score(progress.score, ability.factor),
        progress.next_total,
    )


def abilities_table(
    abilities: Sequence[Ability], virtues_flaws: Sequence[VirtueFlawInstance]
) -> list[AbilityRow]:
    """`abilities` (a character's or a familiar's) as ability_table rows,
    with the bonuses `virtues_flaws` give."""
    rows = []
    for category in ABILITY_CATEGORIES:
        for index, ability in enumerate(abilities):
            if ability.category == category:
                rows.append(_ability_row(virtues_flaws, index, category, ability))
    return rows


def art_info_text(character: Character, art: str) -> str:
    """An Art's details: its score, experience, any bonus, and what it is."""
    score = character.arts.get(art.lower(), ArtScore())
    bonus, bonus_from = scores.art_bonus(character.virtues_flaws, art)
    return "\n".join(
        [
            f"[b]Name:[/] {art} ({ART_ABBREVIATIONS[art]})",
            st.xp_line(score.progress, bonus, bonus_from),
            "",
            f"[b]Description:[/] {ART_DESCRIPTIONS[art]}",
        ]
    )


def known_spell_info_text(saga: Saga, character: Character, index: int) -> str:
    """A known spell's details: the spell, how well the magus casts it, and
    its Mastery."""
    known = character.spells_known[index]
    spell = catalog.find_spell(saga, known.spell_id)
    if spell is None:
        lines = [problem(f"Unknown spell: {escape(known.spell_id)}")]
    else:
        lines = [spl.detail_text(saga, spell), ""]
        lines += ct.known_spell_casting_lines(saga, character, known, spell)
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


def gear_title(character: Character) -> str:
    """Personal Gear's title: how many things, and the character's silver
    when they have any ("Personal Gear (3) · 12 pounds of silver")."""
    title = f"Personal Gear ({len(character.inventory)})"
    if character.silver:
        unit = "pound" if character.silver == 1 else "pounds"
        title += f" · {character.silver} {unit} of silver"
    return title


#: Personal Gear's groups, in display order, with their headers.
INVENTORY_GROUPS: tuple[tuple[str, str], ...] = (
    ("weapon", "Weapons"),
    ("armor", "Armor"),
    ("item", "Other Items"),
)


def inventory_rows(character: Character) -> list[tuple[int | None, str]]:
    """Personal Gear as one list, with a header row (its title and column
    titles) before each kind the character has."""
    rows: list[tuple[int | None, str]] = []
    for kind, header in INVENTORY_GROUPS:
        indexed = [
            (i, item) for i, item in enumerate(character.inventory) if item.kind == kind
        ]
        if not indexed:
            continue
        rows.append((None, pos.group_header(kind, header)))
        for index, item in indexed:
            rows.append((index, pos.row_label(pos.PossessionEntry(kind, item))))
    return rows


def inventory_tables(character: Character) -> list[tuple[str, Table]]:
    """Personal Gear as a table per kind the character has (its title,
    then the kind's columns); choosing a row picks its index in the
    inventory."""
    tables = []
    for kind, header in INVENTORY_GROUPS:
        indexed = [
            (i, item) for i, item in enumerate(character.inventory) if item.kind == kind
        ]
        if indexed:
            tables.append(
                (
                    header,
                    pos.table(
                        kind,
                        [pos.PossessionEntry(kind, item) for _, item in indexed],
                        [i for i, _ in indexed],
                    ),
                )
            )
    return tables


def inventory_item_text(character: Character, index: int) -> str:
    """An item's details; a weapon's also gives its combat totals."""
    item = character.inventory[index]
    text = pos.detail_text(pos.PossessionEntry(item.kind, item))
    if item.kind == "weapon":
        text += "\n\n" + st.combat_text(character, item)
    return text


def subtitle(saga: Saga, character: Character) -> str:
    """The line under the name: what the character is, where and when."""
    house = house_name(character)
    kind = f"Magus of House {house}" if house else character.type.title()
    covenant = saga.covenant(character.covenant_id)
    parts = [kind, covenant.name if covenant else "no covenant"]
    if character.background.setting:
        parts.append(character.background.setting)
    parts.append(f"{saga.current_season} {saga.current_year}")
    return "  ·  ".join(parts)


#: A status's tone, which a front-end draws in its own colour.
GOOD, WARNING, BAD = "success", "warning", "error"


def condition(character: Character) -> list[tuple[str, str]]:
    """The character's Fatigue and wounds in a few words, each with its
    tone: ("Fresh", GOOD), ("2 Light Wounds", WARNING)..."""
    level = character.fatigue_level
    chips = [(level.title(), GOOD if level == "fresh" else WARNING)]
    w = character.wounds
    counts = [
        (w.light, "Light", WARNING),
        (w.medium, "Medium", WARNING),
        (w.heavy, "Heavy", BAD),
    ]
    hurt = [
        (f"{n} {name} Wound{'s' if n > 1 else ''}", tone)
        for n, name, tone in counts
        if n
    ]
    if w.incapacitated:
        hurt.append(("Incapacitated", BAD))
    if w.dead:
        hurt.append(("Dead", BAD))
    penalty = derived.wound_penalty(w, character.virtues_flaws)
    if hurt and penalty:
        hurt.append((f"{penalty:+d} to rolls", BAD))
    return chips + (hurt or [("Unhurt", GOOD)])


@dataclass(frozen=True)
class SpellRow:
    """A known spell as a table row; `index` is into spells_known. A spell
    the saga can't find has only its id as the name."""

    index: int
    name: str
    technique: str
    form: str
    arts: str
    level: int | None
    range: str
    duration: str
    target: str
    ritual: bool
    mastery: int
    #: "Own" for a spell they invented, "Shared" once it is the saga's.
    invented: str = ""


def spell_table(saga: Saga, character: Character) -> list[SpellRow]:
    rows = []
    for index, known in enumerate(character.spells_known):
        spell = catalog.find_spell(saga, known.spell_id)
        if spell is None:
            rows.append(
                SpellRow(
                    index,
                    known.spell_id,
                    "",
                    "",
                    "?",
                    None,
                    "",
                    "",
                    "",
                    False,
                    known.mastery_score,
                )
            )
            continue
        rows.append(
            SpellRow(
                index,
                spell.name,
                spell.technique,
                spell.form,
                spl.shorthand(spell).rsplit(" ", 1)[0],
                spell.level,
                spell.range,
                spell.duration,
                spell.target,
                spell.ritual,
                known.mastery_score,
                spl.invention(saga, character, spell.id),
            )
        )
    return rows


@dataclass(frozen=True)
class VirtueFlawCard:
    """A Virtue or Flaw as a card: its name as taken, tier ("Free" for a
    magus's House Virtue too), category and one-line summary."""

    index: int
    name: str
    tier: str
    category: str
    summary: str


def virtue_flaw_cards(character: Character, side: str) -> list[VirtueFlawCard]:
    """The character's Virtues or Flaws (`side`), Qualities and
    Inferiorities among them, in the order taken."""
    return vf_cards(
        character.virtues_flaws, side, cv.free_benefit(character).free_indices
    )


def vf_cards(
    virtues_flaws: Sequence[VirtueFlawInstance],
    side: str,
    free: Collection[int] = (),
) -> list[VirtueFlawCard]:
    """The Virtues or Flaws (`side`) of `virtues_flaws` as cards, those at
    the `free` indices marked Free."""
    vf_catalog = catalog.load_virtue_flaw_catalog_by_id()
    cards = []
    for index, vf in enumerate(virtues_flaws):
        definition = vf_catalog.get(vf.vf_id)
        if definition is None or definition.side != side:
            continue
        cards.append(
            VirtueFlawCard(
                index,
                catalog.describe_virtue_flaw(vf, vf_catalog),
                "Free" if index in free else definition.tier,
                definition.category_label,
                definition.summary,
            )
        )
    return cards


def virtue_flaw_points(character: Character, side: str) -> float:
    return st.vf_points(
        character.virtues_flaws, side, cv.free_benefit(character).free_indices
    )


def casting_grid(saga: Saga, character: Character) -> dict[tuple[str, str], Breakdown]:
    """Every Technique and Form's Casting Score, with its terms, in the
    magus's home aura."""
    aura, realm = home_aura(saga, character)
    return {
        (technique, form): casting.casting_score(
            character, technique, form, aura=aura, aura_realm=realm
        )
        for technique in TECHNIQUES
        for form in FORMS
    }


def casting_cell_text(score: Breakdown) -> str:
    """One Casting Score's terms and what it casts."""
    lines = []
    for line in score.lines:
        if line.amount is not None:
            lines.append(f"[$label]{escape(line.label)}[/] {line.amount:+g}")
        elif line.multiplier is not None:
            lines.append(f"[$label]{escape(line.label)}[/] x{line.multiplier:g}")
    total = int(score.total)
    return "\n".join(
        [
            *lines,
            "",
            f"[b]Casting Score {total}[/]",
            "",
            "Formulaic: score + die >= level casts it; up to 10 short costs a "
            "Fatigue level.",
            f"Spontaneous: level {total // 5} without Fatigue, "
            "(score + stress die) / 2 with it.",
        ]
    )


# The figures a graphical sheet draws: plain values rather than markup,
# so a front-end can give each its own type and emphasis.


def _fact(label: str, value: object) -> Fact:
    return Fact(label, "" if value is None else str(value))


def glance_facts(saga: Saga, character: Character) -> list[Fact]:
    """Who the character is at a glance: age, covenant, laboratory, type
    and Size, and True Faith when it shows."""
    b = character.background
    covenant = saga.covenant(character.covenant_id)
    facts = [
        _fact("Age", character_age(b.year_born, saga.current_year)),
        _fact(
            tribunal_packages.place_word(saga, covenant).title(),
            covenant.name if covenant else None,
        ),
        *(
            _fact(label, value)
            for label, value in tribunal_packages.magus_facts(saga, character)
        ),
    ]
    if character.type == "magus":
        lab = saga.laboratory(character.assigned_lab_id)
        facts.append(_fact("Laboratory", lab.name if lab else None))
    facts += [
        _fact("Type", character.type.title()),
        *(_fact(label, value) for label, value in animal_facts(character)),
        _fact("Size", st.size_text(character)),
    ]
    if faith.shows_faith(character):
        facts.append(_fact("True Faith", st.faith_score_text(character, saga)))
    elif resistance := penetration.faith_magic_resistance(character, saga):
        facts.append(_fact("Magic Resistance", f"{resistance} (the Dominion)"))
    return facts


def hermetic_facts(character: Character) -> list[Fact]:
    """A magus's House and lineage, as Hermetic Background lists them."""
    h = character.hermetic
    return [
        _fact("House", house_name(character)),
        _fact("Domus Magna", h.domus_magna),
        _fact("Primus", h.primus),
        _fact("Parens", h.parens),
        _fact("Covenant of Apprenticeship", h.covenant_of_apprenticeship),
        _fact("Age of Apprenticeship", h.age_of_apprenticeship),
    ]


def biographical_facts(saga: Saga, character: Character) -> list[Fact]:
    """Biographical Detail's short fields; the physical description and
    Biography are prose and drawn apart."""
    b, d = character.background, character.description
    facts = [_fact("Player", b.player)]
    if saga.players:  # a hosted saga's sign-in
        player = pl.player_by_id(saga, b.player_id)
        facts.append(_fact("Played by", player.name if player else None))
    return [
        *facts,
        _fact("Birth Name", b.birth_name),
        _fact("Year Born", b.year_born),
        _fact("Race/Nationality", b.race_nationality),
        _fact("Place of Origin", b.place_of_origin),
        _fact("Religion", b.religion),
        _fact("Title/Profession", b.title_profession),
        _fact("Height", d.height),
        _fact("Weight", d.weight),
        _fact("Hair", d.hair),
        _fact("Eyes", d.eyes),
        _fact("Handedness", d.handedness.title()),
    ]


def aging_facts(character: Character) -> list[Fact]:
    """The aging roll's figures, once there are any."""
    a = character.aging
    facts = []
    if a.apparent_age is not None:
        facts.append(_fact("Apparent Age", a.apparent_age))
    for name, points in a.aging_points.items():
        if points:
            facts.append(_fact(f"{name.title()} Aging Points", points))
    if a.longevity_modifier:
        facts.append(_fact("Longevity Ritual", f"-{a.longevity_modifier} to aging"))
        if a.longevity_effects:
            facts.append(
                _fact(
                    "Its experimental effects",
                    "; ".join(experiment.describe(e) for e in a.longevity_effects),
                )
            )
    if a.recovering:
        facts.append(_fact("Recovering", a.recovering))
    return facts


@dataclass(frozen=True)
class Dial:
    """A score that rises as points gather: `points` of the `span` the next
    score needs (span 0 at the top score). `top` is the score that ends
    the character's story (Warping 10, Decrepitude 5)."""

    score: int
    points: int
    span: int
    top: int

    @property
    def fraction(self) -> float:
        """The way to the next score, from 0 to 1."""
        return min(self.points / self.span, 1.0) if self.span else 1.0


def warping_dial(character: Character) -> Dial:
    a = character.aging
    score = a.warping_score
    span = warping.points_for(score + 1) - warping.points_for(score)
    return Dial(score, a.warping_points, span, WARPING_TOP)


def decrepitude_dial(character: Character) -> Dial:
    a = character.aging
    score = max(0, min(a.decrepitude, DECREPITUDE_TOP))
    base = aging.points_for_score(score)
    span = 0 if score >= DECREPITUDE_TOP else aging.points_for_score(score + 1) - base
    return Dial(score, max(0, a.decrepitude_points - base), span, DECREPITUDE_TOP)


#: Warping 10 is Final Twilight; Decrepitude 5, death from old age.
WARPING_TOP, DECREPITUDE_TOP = 10, 5


@dataclass(frozen=True)
class WoundBand:
    """One column of the Damage Table: the wound, the damage it takes
    (`high` None for Dead), how many the character has and each one's
    penalty (None where a wound ends acting rather than penalising it)."""

    name: str
    low: int
    high: int | None
    count: int
    penalty: int | None


def wound_track(character: Character) -> list[WoundBand]:
    """The Damage Table for the character's Size, with their wounds."""
    return damage_table(character.wounds, int(derived.size(character).total))


def damage_table(w: Wounds, size: int) -> list[WoundBand]:
    """The Damage Table for `size`, with wounds `w`."""
    counts = {
        "Light": w.light,
        "Medium": w.medium,
        "Heavy": w.heavy,
        "Incapacitating": int(w.incapacitated),
        "Dead": int(w.dead),
    }
    return [
        WoundBand(
            name,
            low,
            high,
            counts[name],
            derived.WOUND_PENALTIES.get(name.lower()),
        )
        for name, low, high in derived.wound_ranges(size)
    ]


def fatigue_track(character: Character) -> list[tuple[str, int, bool]]:
    """Each Fatigue level as (name, penalty, whether it is the current
    one), Fresh first."""
    return fatigue_levels(character.fatigue_level, character.virtues_flaws)


def fatigue_levels(
    current: str, virtues_flaws: Sequence[VirtueFlawInstance]
) -> list[tuple[str, int, bool]]:
    """fatigue_track for anyone at Fatigue level `current`."""
    return [
        (
            level.title(),
            derived.fatigue_penalty(level, virtues_flaws),
            level == current,
        )
        for level in derived.FATIGUE_PENALTIES
    ]


def health_facts(character: Character, saga: Saga | None = None) -> list[Fact]:
    """Soak, Encumbrance and the penalties wounds and Fatigue give, then
    what the wounds carry and how they recover."""
    soak = derived.soak(character)
    load = derived.carried_load(character.inventory)
    encumbrance = derived.encumbrance(load, character.characteristics.strength)
    wounds = derived.wound_penalty(character.wounds, character.virtues_flaws)
    fatigue = derived.fatigue_penalty(character.fatigue_level, character.virtues_flaws)
    return [
        _fact("Soak", int(soak.total)),
        _fact("Encumbrance", encumbrance),
        _fact("Wound Penalty", f"{wounds:+d}"),
        _fact("Total Penalty", f"{wounds + fatigue:+d}"),
        *(
            _fact(label, value)
            for label, value in (
                line.split(": ", 1) for line in st.recovery_lines(saga, character)
            )
        ),
    ]


# -- a Line or Sketch character --

#: Said under a sketch's Abilities: the rule for those it doesn't list.
UNLISTED_ABILITIES = "Abilities not listed count as 0."


def has_statblock(character: Character) -> bool:
    """Whether the sheet opens on a statblock: a Line or Sketch character,
    whose sheet leaves out what only play needs (Inventory, Planning)."""
    return character.detail != FULL


def statblock(saga: Saga, character: Character) -> list[tuple[str, str]]:
    """A Line or Sketch character as the books print an NPC: (heading,
    markup) pairs, each left out while it is empty. A Line character has
    only who they are; a Sketch has the scores play needs."""
    summary = (
        escape(character.summary)
        if character.summary
        else "[$label]Not written yet: Edit the character to say.[/]"
    )
    block = [("In the Saga", summary)]
    if character.detail == LINE:
        return block
    c = character.characteristics
    block.append(
        (
            "Characteristics",
            ", ".join(
                f"{label} {signed(value)}"
                for label, value in (
                    ("Int", c.intelligence),
                    ("Per", c.perception),
                    ("Pre", c.presence),
                    ("Com", c.communication),
                    ("Str", c.strength),
                    ("Sta", c.stamina),
                    ("Dex", c.dexterity),
                    ("Qik", c.quickness),
                )
            ),
        )
    )
    if character.type == "magus":
        arts = sorted(
            (row for row in art_rows(character, (*TECHNIQUES, *FORMS)) if row.xp),
            key=lambda row: -character.arts[row.art.lower()].level,
        )
        if arts:
            block.append(("Arts", ", ".join(f"{row.art} {row.score}" for row in arts)))
    abilities = [
        f"{escape(row.name)} {row.score}"
        + (f" ({escape(row.specialty)})" if row.specialty else "")
        for row in ability_table(character)
    ]
    block.append(
        (
            "Abilities",
            (", ".join(abilities) + "\n" if abilities else "")
            + f"[$label]{UNLISTED_ABILITIES}[/]",
        )
    )
    virtues_flaws = [
        f"{escape(card.name)} ({card.tier})"
        for side in ("Virtue", "Flaw")
        for card in virtue_flaw_cards(character, side)
    ]
    if virtues_flaws:
        block.append(("Virtues and Flaws", ", ".join(virtues_flaws)))
    spells = [
        escape(row.name)
        + (f" {row.arts} {row.level}" if row.level is not None else "")
        + (f" (Mastery {row.mastery})" if row.mastery else "")
        for row in spell_table(saga, character)
    ]
    if spells:
        block.append(("Signature Spells", ", ".join(spells)))
    for heading, traits in (
        ("Personality", character.personality_traits),
        ("Reputations", character.reputations),
    ):
        if traits:
            block.append(
                (heading, ", ".join(label for _, label in st.trait_rows(traits)))
            )
    return block


def statblock_text(saga: Saga, character: Character) -> str:
    """The statblock as one block of markup: each heading in the label
    colour over its line."""
    return "\n\n".join(
        f"[b $label]{heading}[/]\n{words}"
        for heading, words in statblock(saga, character)
    )
