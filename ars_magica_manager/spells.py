"""Logic behind spells -- no UI in here.

Where a spell id resolves to (the shared catalog, the saga's own spells, a
magus's invented spells), the figures worked out from a spell (magnitude, the
"CrIg 20" shorthand, a Ritual's vis cost and casting time), and reading the
Range/Duration/Target notation the rulebook and the Grand Grimoire use.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import catalog, storage
from .csv_import import parse_rows, read_text_any, skipped_preview
from .markup import escape, fit
from .models import (
    ART_ABBREVIATIONS,
    ART_LOOKUP,
    FORMS,
    SPELL_DURATIONS,
    SPELL_RANGES,
    SPELL_SOURCES,
    SPELL_TARGETS,
    TECHNIQUES,
    Saga,
    Spell,
)

# ------------------------------------------------------------ where they live


def find_spell(saga: Saga, spell_id: str | None) -> Spell | None:
    """The spell with this id, wherever it lives: the shared catalog, then the
    saga's own spells, then any magus's invented spells."""
    if not spell_id:
        return None
    found = catalog.load_spell_catalog_by_id().get(spell_id)
    if found is not None:
        return found
    for spell in saga.spells:
        if spell.id == spell_id:
            return spell
    for character in saga.characters:
        for spell in character.invented_spells:
            if spell.id == spell_id:
                return spell
    return None


def _name_key(name: str) -> str:
    return " ".join(name.replace("’", "'").lower().split())


def find_spell_by_name(saga: Saga, name: str) -> Spell | None:
    """The spell with this name (any case, typographic apostrophes allowed),
    wherever it lives: the catalog, then the saga's own, then any magus's
    invented spells. How a book whose spell was typed (or imported) links."""
    key = _name_key(name)
    if not key:
        return None
    for spell in catalog.load_spell_catalog():
        if _name_key(spell.name) == key:
            return spell
    for spell in saga.spells:
        if _name_key(spell.name) == key:
            return spell
    for character in saga.characters:
        for spell in character.invented_spells:
            if _name_key(spell.name) == key:
                return spell
    return None


def pickable_spells(saga: Saga) -> list[tuple[Spell, str]]:
    """Every spell a book or a magus can point at, with where it's from:
    the catalog, the saga's own, then each magus's invented spells."""
    found = [(s, s.source) for s in catalog.load_spell_catalog()]
    found += [(s, "Saga") for s in saga.spells]
    for character in saga.characters:
        found += [(s, f"{character.name}'s") for s in character.invented_spells]
    return found


def all_spell_ids(saga: Saga) -> set[str]:
    """Every spell id in use, for generating a new unique one."""
    ids = set(catalog.load_spell_catalog_by_id())
    ids.update(s.id for s in saga.spells)
    ids.update(s.id for c in saga.characters for s in c.invented_spells)
    return ids


# ------------------------------------------------------------------ figures


def magnitude(spell: Spell) -> int | None:
    """Level / 5, rounded up (levels 1-5 are magnitude 1); None for a General
    spell, whose magnitude depends on the level it's cast at."""
    if spell.level is None:
        return None
    return max(1, math.ceil(spell.level / 5))


def shorthand(spell: Spell) -> str:
    """Standard Hermetic notation: "CrIg 20", "Mu(Re)Te 15", "ReCo(Me) 10",
    "ReVi Gen". A requisite Technique follows the Technique and a requisite
    Form follows the Form."""

    def abbr(art: str) -> str:
        return ART_ABBREVIATIONS.get(art, art[:2])

    technique_reqs = [r for r in spell.requisites if r in TECHNIQUES]
    form_reqs = [r for r in spell.requisites if r not in TECHNIQUES]

    def reqs(arts: list[str]) -> str:
        return f"({'/'.join(abbr(a) for a in arts)})" if arts else ""

    arts = (
        f"{abbr(spell.technique)}{reqs(technique_reqs)}"
        f"{abbr(spell.form)}{reqs(form_reqs)}"
    )
    return f"{arts} {'Gen' if spell.level is None else spell.level}"


def vis_cost(spell: Spell) -> int | None:
    """Pawns of vis a Ritual needs: one per magnitude (0 for a Formulaic
    spell; None for a General Ritual, which depends on the level cast)."""
    if not spell.ritual:
        return 0
    return magnitude(spell)


def casting_time(spell: Spell) -> str:
    """A Formulaic spell takes a round; a Ritual 15 minutes per magnitude."""
    if not spell.ritual:
        return "1 round"
    mag = magnitude(spell)
    if mag is None:
        return "15 minutes per magnitude"
    return f"{mag * 15} minutes"


# ------------------------------------------------- Range / Duration / Target

#: Abbreviations and variant spellings used by the rulebook and the Grand
#: Grimoire, mapped to the standard names (lower case keys).
_RANGE_NAMES = {r.lower(): r for r in SPELL_RANGES} | {
    "per": "Personal",
    "pers": "Personal",
    "arc": "Arcane Connection",
    "arcane": "Arcane Connection",
    "arcane connection": "Arcane Connection",
}
_DURATION_NAMES = {d.lower(): d for d in SPELL_DURATIONS} | {
    "mom": "Momentary",
    "conc": "Concentration",
    "diam": "Diameter",
    "spec": "Special",
    "special": "Special",
}
_TARGET_NAMES = {t.lower(): t for t in SPELL_TARGETS} | {
    "ind": "Individual",
    "indiv": "Individual",
    "bound": "Boundary",
    "str": "Structure",
    "spec": "Special",
    "special": "Special",
}


def _normalise(value: str, names: dict[str, str]) -> str:
    cleaned = value.strip().strip(".").strip()
    return names.get(cleaned.lower(), cleaned)


def normalise_range(value: str) -> str:
    return _normalise(value, _RANGE_NAMES)


def normalise_duration(value: str) -> str:
    return _normalise(value, _DURATION_NAMES)


def normalise_target(value: str) -> str:
    return _normalise(value, _TARGET_NAMES)


def _requisite_tokens(text: str) -> list[str]:
    return [
        t.strip().strip(".")
        for t in re.split(r"[,;/&]|\band\b|\s+", text)
        if t.strip().strip(".")
    ]


def unknown_requisites(text: str) -> list[str]:
    """The words of a typed requisites list that aren't Arts ("Magic" in
    "Rego Magic"), for rejecting user input."""
    return [t for t in _requisite_tokens(text) if t.lower() not in ART_LOOKUP]


def parse_requisites(text: str) -> list[str]:
    """The Arts named in a requisites list ("Rego", "Perdo, Corpus", "Au/Im"),
    in order; anything that isn't an Art is ignored."""
    found = []
    for token in re.split(r"[,;/&]|\band\b|\s+", text):
        art = ART_LOOKUP.get(token.strip().strip(".").lower())
        if art and art not in found:
            found.append(art)
    return found


_RDT = re.compile(r"^\s*R:\s*(?P<r>[^,]+),\s*D:\s*(?P<d>[^,]+),\s*T:\s*(?P<rest>.+)$")
_REQUISITE = re.compile(r"\bReq(?:uisites?)?\s*:\s*(?P<arts>.*)$", re.IGNORECASE)


def parse_rdt(line: str) -> dict | None:
    """Read an "R: Voice, D: Mom, T: Ind, Ritual; Req: Rego" line into range,
    duration, target, ritual and requisites; None if it isn't one."""
    match = _RDT.match(line)
    if match is None:
        return None
    rest = match.group("rest")
    requisites: list[str] = []
    req = _REQUISITE.search(rest)
    if req is not None:
        requisites = parse_requisites(req.group("arts"))
        rest = rest[: req.start()]
    ritual = bool(re.search(r"\bRitual\b", rest, re.IGNORECASE))
    rest = re.sub(r"\bRitual\b", "", rest, flags=re.IGNORECASE)
    target = re.split(r"[,;]", rest)[0]
    return {
        "range": normalise_range(match.group("r")),
        "duration": normalise_duration(match.group("d")),
        "target": normalise_target(target),
        "ritual": ritual,
        "requisites": requisites,
    }


# ------------------------------------------------------------ the list view

#: The short forms used in a list row ("Voice/Mom/Ind").
_SHORT_NAMES = {
    "Personal": "Per",
    "Arcane Connection": "Arc",
    "Momentary": "Mom",
    "Concentration": "Conc",
    "Diameter": "Diam",
    "Individual": "Ind",
    "Structure": "Str",
    "Boundary": "Bound",
}

#: The Source filter's value for the saga's own spells.
OWN_SOURCE = "__own__"


def all_spells(saga: Saga) -> list[Spell]:
    """What the Spells view lists: the catalog, then the saga's own spells."""
    return catalog.load_spell_catalog() + list(saga.spells)


def is_own(saga: Saga, spell: Spell) -> bool:
    """A spell of the saga's own (editable), rather than the catalog's."""
    return any(s is spell for s in saga.spells)


def filter_spells(
    saga: Saga,
    spells: list[Spell],
    *,
    text: str = "",
    technique: str | None = None,
    form: str | None = None,
    ritual: bool | None = None,
    source: str | None = None,
    min_level: int | None = None,
    max_level: int | None = None,
) -> list[Spell]:
    """The spells that pass every filter given. `text` matches the name or the
    description, every word of it (in any order, any case). `form` also
    matches a requisite Form, `technique` a requisite Technique. A General
    spell passes any level range. `source` is a SPELL_SOURCES key, or
    OWN_SOURCE for the saga's own."""
    words = text.lower().split()
    shown = []
    for spell in spells:
        if words:
            haystack = f"{spell.name} {spell.description}".lower()
            if not all(word in haystack for word in words):
                continue
        if technique and technique not in (spell.technique, *spell.requisites):
            continue
        if form and form not in (spell.form, *spell.requisites):
            continue
        if ritual is not None and spell.ritual != ritual:
            continue
        if source == OWN_SOURCE and not is_own(saga, spell):
            continue
        if (
            source
            and source != OWN_SOURCE
            and (is_own(saga, spell) or spell.source != source)
        ):
            continue
        if spell.level is not None:
            if min_level is not None and spell.level < min_level:
                continue
            if max_level is not None and spell.level > max_level:
                continue
        shown.append(spell)
    return shown


def _short(value: str) -> str:
    return _SHORT_NAMES.get(value, value)


_NAME_WIDTH = 30
_ARTS_WIDTH = 16
_LEVEL_WIDTH = 5
_RDT_WIDTH = 22
_RITUAL_WIDTH = 7


def arts(spell: Spell) -> str:
    """The shorthand without the level: "Mu(Re)Te"."""
    return shorthand(spell).rsplit(" ", 1)[0]


def table_header() -> str:
    """Column titles over the list; the two-character indent is the list's
    selector marker."""
    return (
        f"  {'Name':<{_NAME_WIDTH}} {'Arts':<{_ARTS_WIDTH}}{'Level':>{_LEVEL_WIDTH}}  "
        f"{'Range/Duration/Target':<{_RDT_WIDTH}} {'Ritual':<{_RITUAL_WIDTH}}Source"
    )


def row_label(saga: Saga, spell: Spell) -> str:
    """One list row (markup), lined up with `table_header`."""
    level = "Gen" if spell.level is None else str(spell.level)
    rdt = (
        "(details missing)"
        if spell.details_missing
        else "/".join(_short(v) for v in (spell.range, spell.duration, spell.target))
    )
    source = "Saga" if is_own(saga, spell) else spell.source
    return (
        f"{escape(fit(spell.name, _NAME_WIDTH))} {escape(fit(arts(spell), _ARTS_WIDTH))}"
        f"{level:>{_LEVEL_WIDTH}}  {escape(fit(rdt, _RDT_WIDTH))} "
        f"{('Ritual' if spell.ritual else ''):<{_RITUAL_WIDTH}}{escape(source)}"
    )


def detail_text(saga: Saga, spell: Spell | None) -> str:
    """The details panel (markup): everything about the spell, the figures
    worked out from it, then its description."""
    if spell is None:
        return "[dim]Select a spell to see its details.[/]"

    def line(label: str, value: object) -> str:
        return f"[b]{label}:[/] {escape(str(value))}"

    mag = magnitude(spell)
    lines = [
        f"[b]{escape(spell.name)}[/]  {escape(shorthand(spell))}"
        + ("  [b]Ritual[/]" if spell.ritual else ""),
    ]
    if spell.details_missing:
        lines.append("[dim]The source lists this spell without its details.[/]")
    else:
        lines.append(
            line("Range", spell.range)
            + "   "
            + line("Duration", spell.duration)
            + "   "
            + line("Target", spell.target)
        )
    level = (
        "General (cast at any level)"
        if spell.level is None
        else f"{spell.level} (magnitude {mag})"
    )
    parts = [line("Level", level)]
    if spell.base_level is not None:
        parts.append(line("Base", spell.base_level))
    if spell.requisites:
        parts.append(line("Requisites", ", ".join(spell.requisites)))
    lines.append("   ".join(parts))
    if spell.ritual:
        vis = vis_cost(spell)
        vis_text = "1 pawn per magnitude" if vis is None else f"{vis} pawn(s)"
        lines.append(
            line("Vis", vis_text) + "   " + line("Casting time", casting_time(spell))
        )
    if is_own(saga, spell):
        origin = f"The saga's own spell{f' ({spell.source})' if spell.source else ''}"
        lines.append(f"[dim]{escape(origin)} -- press e to edit it.[/]")
    else:
        book = SPELL_SOURCES.get(spell.source, spell.source)
        lines.append(f"[dim]From {escape(book)} (catalog spell, read-only).[/]")
    if spell.description.strip():
        lines += ["", escape(spell.description.strip())]
    return "\n".join(lines)


# ------------------------------------------------------------- CSV import

#: Columns a spell import reads (any case, any order); `name`, `technique` and
#: `form` are required.
CSV_COLUMNS: tuple[str, ...] = (
    "name",
    "technique",
    "form",
    "level",
    "requisites",
    "range",
    "duration",
    "target",
    "ritual",
    "base_level",
    "description",
    "source",
)

#: What each column holds, for the Import Spells helper.
CSV_COLUMN_HELP: tuple[tuple[str, str], ...] = (
    ("name", "the spell's name (required)"),
    ("technique", "Creo, Intellego, Muto, Perdo or Rego, or Cr/In/Mu/Pe/Re (required)"),
    ("form", "one of the ten Forms, or its abbreviation (required)"),
    ("level", "a number, or Gen (or blank) for a General spell"),
    ("requisites", "extra Arts, e.g. Rego, Corpus"),
    ("range", "Personal, Touch, Eye, Voice, Sight, Arcane Connection (or Per, Arc...)"),
    (
        "duration",
        "Momentary, Concentration, Diameter, Sun, Ring, Moon, Year (or Mom...)",
    ),
    (
        "target",
        "Individual, Circle, Part, Group, Room, Structure, Boundary, a sense...",
    ),
    ("ritual", "yes or no (blank is no)"),
    ("base_level", "the guideline level before R/D/T (optional)"),
    ("description", "the spell's effect"),
    ("source", "where it's from, e.g. a house rule"),
)

#: The file "Save example CSV" writes.
EXAMPLE_CSV = (
    "name,technique,form,level,requisites,range,duration,target,ritual,"
    "base_level,description,source\n"
    "Palm of Warming Flame,Creo,Ignem,5,,Touch,Diameter,Individual,no,2,"
    '"A gentle flame dances in your palm, warming but never burning.",House rule\n'
    "Ward of the Quiet Hearth,Rego,Vim,Gen,Mentem,Touch,Year,Boundary,yes,,"
    '"A general ward over the covenant hall, cast at any level.",House rule\n'
)

_YES = {"yes", "y", "true", "1", "x", "ritual"}
_NO = {"", "no", "n", "false", "0", "formulaic"}


@dataclass
class SpellCsvImport:
    """What a spell CSV holds: the spells (not yet given ids), the rows that
    couldn't be read and why, and the columns that weren't used."""

    spells: list[Spell] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    unused_columns: list[str] = field(default_factory=list)


def _art(raw: str, kind: tuple[str, ...], label: str) -> str:
    art = ART_LOOKUP.get(raw.strip().lower())
    if art is None or art not in kind:
        if raw.strip():
            raise ValueError(f"unknown {label} {raw.strip()!r}")
        raise ValueError(f"no {label}")
    return art


def _spell_from_row(row: dict[str, str]) -> Spell:
    """One CSV row as a Spell, or ValueError saying what's wrong with it."""
    name = row.get("name", "").strip()
    if not name:
        raise ValueError("no name")
    level_text = row.get("level", "").strip()
    if level_text.lower() in ("", "gen", "general"):
        level = None
    else:
        try:
            level = int(level_text)
        except ValueError:
            raise ValueError(f"Level {level_text!r} isn't a number or Gen") from None
        if level < 1:
            raise ValueError("a Level below 1")
    requisites_text = row.get("requisites", "")
    requisites = parse_requisites(requisites_text)
    if unknown_requisites(requisites_text):
        raise ValueError(f"requisites {requisites_text.strip()!r} aren't all Arts")
    ritual_text = row.get("ritual", "").strip().lower()
    if ritual_text not in _YES | _NO:
        raise ValueError(f"Ritual {row.get('ritual', '').strip()!r} isn't yes or no")
    base_text = row.get("base_level", "").strip()
    try:
        base_level = int(base_text) if base_text else None
    except ValueError:
        raise ValueError(f"base level {base_text!r} isn't a number") from None
    return Spell(
        id="",
        name=name,
        technique=_art(row.get("technique", ""), TECHNIQUES, "Technique"),
        form=_art(row.get("form", ""), FORMS, "Form"),
        level=level,
        requisites=requisites,
        range=normalise_range(row.get("range", "")),
        duration=normalise_duration(row.get("duration", "")),
        target=normalise_target(row.get("target", "")),
        ritual=ritual_text in _YES,
        base_level=base_level,
        description=row.get("description", "").strip(),
        source=row.get("source", "").strip(),
    )


def parse_spells_csv(text: str) -> SpellCsvImport:
    """Read spells from CSV text with a header row (see CSV_COLUMNS). Raises
    ValueError without a name, technique or form column; a bad row is skipped
    and reported, not fatal."""
    spells, skipped, unused = parse_rows(
        text, ("name", "technique", "form"), CSV_COLUMNS, _spell_from_row
    )
    return SpellCsvImport(spells, skipped, unused)


def read_spells_csv(path: Path) -> SpellCsvImport:
    """parse_spells_csv on a file (UTF-8, with or without a byte-order mark,
    or Windows-1252)."""
    return parse_spells_csv(read_text_any(path))


def spell_import_preview(
    result: SpellCsvImport, file_name: str, existing_names: set[str]
) -> str:
    """The confirmation shown before importing spells (markup)."""
    count = len(result.spells)
    lines = [
        f"Import {count} spell{'s' if count != 1 else ''} from "
        f"[b]{escape(file_name)}[/] into the saga's own spells?"
    ]
    if result.unused_columns:
        lines.append(
            "[dim]Unrecognised columns ignored: "
            f"{escape(', '.join(result.unused_columns))}.[/]"
        )
    seen = {n.lower() for n in existing_names}
    repeats = 0
    for spell in result.spells:
        if spell.name.lower() in seen:
            repeats += 1
        seen.add(spell.name.lower())
    if repeats:
        verb = "has" if repeats == 1 else "have"
        lines.append(
            f"{repeats} {verb} the same name as another spell; you'll be asked "
            "whether to add or skip each."
        )
    general = sum(1 for s in result.spells if s.level is None)
    if general:
        lines.append(f"[dim]{general} General-level (no level given).[/]")
    lines += skipped_preview(result.skipped)
    return "\n".join(lines)


# ------------------------------------------------------------------ adding


def _own_spell_id(name: str, taken: set[str]) -> str:
    """The saga's own spells get ids like "saga_pilum_of_fire", so they
    can't clash with the catalog's "spell_..." ids."""
    return storage.generate_unique_id(f"saga {name}", taken)


def add_own_spell(saga: Saga, name: str, technique: str, form: str) -> Spell:
    """A new spell of the saga's own, added to `saga.spells`."""
    spell = Spell(
        id=_own_spell_id(name, all_spell_ids(saga)),
        name=name,
        technique=technique,
        form=form,
    )
    saga.spells.append(spell)
    return spell


def add_imported_spells(saga: Saga, spells: list[Spell]) -> None:
    """Give imported spells ids of the saga's own and add them."""
    ids = all_spell_ids(saga)
    for spell in spells:
        spell.id = _own_spell_id(spell.name, ids)
        ids.add(spell.id)
        saga.spells.append(spell)
