"""What the Character sheet shows, independent of how it is drawn.

Each function returns one section's text (in the app's markup, see
markup.py) or its rows, from the saga and the character; a front-end lays
them out. The terminal and desktop sheets both read these, so the two
cannot disagree about what a character's sheet says.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from . import casting_text as ct
from . import catalog, faith
from . import lab_texts as lt
from . import players as pl
from . import possessions as pos
from . import sheet_text as st
from . import spells as spl
from .arts import ART_ABBREVIATIONS, ART_DESCRIPTIONS
from .markup import aligned, escape, inherited, problem
from .models import ArtScore, Character, Saga, character_age
from .rules import scores


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
    ]
    if faith.shows_faith(character):
        rows += [
            ("True Faith Score", st.faith_score_text(character)),
            ("Faith Points", str(b.faith_points)),
        ]
    rows.append(("Size", st.size_text(character)))
    return aligned(rows)


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
            f"Physical Description: {escape(d.physical_description) or '(not set)'}",
        ]
    )


def biographical_right_text(character: Character) -> str:
    """Biographical Detail's second column: the free-text Biography."""
    return escape(character.description.biography) or "(none recorded)"


def aging_text(character: Character) -> str:
    """Aging & Warping: Decrepitude, the aging roll's figures and Warping."""
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
    if a.recovering:
        lines.append(f"Recovering from an Aging Crisis: {a.recovering}")
    return "\n".join(
        [
            *lines,
            "Effects of Aging:",
            escape(a.effects) or "(none recorded)",
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


@dataclass(frozen=True)
class ArtRow:
    """One Art's line on the sheet: its score as shown (with any bonus, as
    "10 (13)") and its experience."""

    art: str
    abbreviation: str
    score: str
    xp: int


def art_row(character: Character, art: str) -> ArtRow:
    score = character.arts.get(art.lower(), ArtScore())
    bonus, _ = scores.art_bonus(character.virtues_flaws, art)
    return ArtRow(
        art, ART_ABBREVIATIONS[art], st.adjusted_score(score.level, bonus), score.xp
    )


def art_rows(character: Character, arts: Sequence[str]) -> list[ArtRow]:
    return [art_row(character, art) for art in arts]


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
    spell = spl.find_spell(saga, known.spell_id)
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


def inventory_item_text(character: Character, index: int) -> str:
    """An item's details; a weapon's also gives its combat totals."""
    item = character.inventory[index]
    text = pos.detail_text(pos.PossessionEntry(item.kind, item))
    if item.kind == "weapon":
        text += "\n\n" + st.combat_text(character, item)
    return text
