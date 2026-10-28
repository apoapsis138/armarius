"""Charters to start a covenant's own from: the book's Charter of Arae
Flaviae (Covenants pp. 33, 125-128, data/charter_template_catalog.json)
and the ones the troupe saves, kept with the saga, each suited to any
Tribunal or to one Tribunal's customs.

Pattern: Prototype. A template is copied into the covenant's charter,
its {covenant}, {tribunal} and {year} filled in, and edited from there;
in Python that is plain data copied with `dataclasses.replace`. A charter
drawn from a template the Quaesitores ratify at once (Arae Flaviae) is
ratified while it stands as the template wrote it: `unaltered` compares
it with the template filled in afresh."""

from __future__ import annotations

import json
from dataclasses import replace
from functools import lru_cache
from pathlib import Path

from . import DATA_DIR, storage
from .models import (
    CLAUSE_IN_FORCE,
    CharterClause,
    CharterTemplate,
    Covenant,
    CovenantCharter,
    Saga,
)

CATALOG_PATH = DATA_DIR / "charter_template_catalog.json"

#: The book's model charter.
ARAE_FLAVIAE = "arae_flaviae"


@lru_cache(maxsize=4)
def _catalog(path: Path) -> tuple[CharterTemplate, ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return tuple(CharterTemplate.from_dict(e) for e in data["entries"])


def book_templates(path: Path = CATALOG_PATH) -> tuple[CharterTemplate, ...]:
    """The templates the books give (the Charter of Arae Flaviae)."""
    return _catalog(path)


def tribunal_key(saga: Saga, covenant: Covenant) -> str:
    """The covenant's Tribunal's package key ("" with no Tribunal)."""
    tribunal = saga.tribunal(covenant.tribunal_id)
    return tribunal.package if tribunal is not None else ""


def offered(saga: Saga, covenant: Covenant) -> list[CharterTemplate]:
    """The templates the covenant may start from: those for its
    Tribunal's customs first, then those for any Tribunal (the book's
    before the saga's); those for other Tribunals' customs last."""
    every = [*book_templates(), *saga.charter_templates]
    key = tribunal_key(saga, covenant)
    own = [t for t in every if t.tribunal and t.tribunal == key]
    general = [t for t in every if not t.tribunal]
    others = [t for t in every if t.tribunal and t.tribunal != key]
    return own + general + others


def find(saga: Saga, template_id: str) -> CharterTemplate | None:
    return next(
        (
            t
            for t in [*book_templates(), *saga.charter_templates]
            if t.id == template_id
        ),
        None,
    )


def region_name(saga: Saga, covenant: Covenant) -> str:
    """The covenant's Tribunal as "the Tribunal of ..." names it: "The
    Rhine Tribunal" is "Rhine" ("" with no Tribunal)."""
    tribunal = saga.tribunal(covenant.tribunal_id)
    if tribunal is None:
        return ""
    name = tribunal.name.strip()
    name = name.removeprefix("The ").removesuffix(" Tribunal").strip()
    return name.removeprefix("Tribunal of ").strip()


def _blanks(saga: Saga, covenant: Covenant, year: int | None) -> dict[str, str]:
    return {
        "covenant": covenant.name,
        "tribunal": region_name(saga, covenant),
        "year": str(year) if year is not None else "",
    }


def _fill(words: str, blanks: dict[str, str]) -> str:
    """The words with their blanks filled; a blank the words don't know
    stays as written."""
    for key, value in blanks.items():
        words = words.replace("{" + key + "}", value)
    return words


def drawn(
    saga: Saga, covenant: Covenant, template: CharterTemplate, year: int | None
) -> CovenantCharter:
    """The charter the template makes for the covenant, sworn in `year`:
    its name, preamble and clauses, each clause agreed that year and in
    force. Seals and the Official Seal are the covenant's own."""
    blanks = _blanks(saga, covenant, year)
    return CovenantCharter(
        name=_fill(template.charter_name or template.name, blanks),
        preamble=_fill(template.preamble, blanks),
        year=year,
        template=template.id,
        probation_seasons=template.probation_seasons,
        clauses=[
            CharterClause(
                c.number,
                _fill(c.text, blanks),
                year=year,
                section=c.section,
            )
            for c in template.clauses
        ],
    )


def use(
    saga: Saga, covenant: Covenant, template: CharterTemplate, year: int | None
) -> None:
    """Draw the covenant's charter from the template, keeping its seals and
    Official Seal: the clauses and preamble it had are replaced."""
    old = covenant.charter_of_covenant
    made = drawn(saga, covenant, template, year)
    covenant.charter_of_covenant = replace(
        made,
        season=old.season,
        ratified=old.ratified,
        notarized_by=old.notarized_by,
        notarized_year=old.notarized_year,
        notarized_season=old.notarized_season,
        reviewed=old.reviewed,
        seals=old.seals,
    )


def unaltered(saga: Saga, covenant: Covenant) -> bool:
    """Whether the covenant's charter still stands as its template wrote
    it: the same preamble, and the same clauses in the same order, none
    amended or broken."""
    charter = covenant.charter_of_covenant
    template = find(saga, charter.template) if charter.template else None
    if template is None:
        return False
    fresh = drawn(saga, covenant, template, charter.year)
    if charter.preamble.strip() != fresh.preamble.strip():
        return False
    if len(charter.clauses) != len(fresh.clauses):
        return False
    return all(
        (c.number, c.section, c.text.strip(), c.status)
        == (f.number, f.section, f.text.strip(), CLAUSE_IN_FORCE)
        for c, f in zip(charter.clauses, fresh.clauses, strict=True)
    )


def ratified_at_once(saga: Saga, covenant: Covenant) -> CharterTemplate | None:
    """The template whose unaltered use the Quaesitores ratify at once
    (Covenants p. 33), while the charter stands as it wrote it."""
    charter = covenant.charter_of_covenant
    template = find(saga, charter.template) if charter.template else None
    if template is None or not template.ratified_unaltered:
        return None
    return template if unaltered(saga, covenant) else None


def save_as(
    saga: Saga, covenant: Covenant, name: str, tribunal: str
) -> CharterTemplate:
    """Keep the covenant's charter with the saga as a template named
    `name`, for `tribunal`'s customs ("" for any); one of the same name is
    replaced. The covenant's and its Tribunal's names become blanks again,
    so the template reads true for another covenant."""
    charter = covenant.charter_of_covenant
    region = region_name(saga, covenant)

    def blank(words: str) -> str:
        words = words.replace(covenant.name, "{covenant}") if covenant.name else words
        return words.replace(region, "{tribunal}") if region else words

    existing = next((t for t in saga.charter_templates if t.name == name), None)
    template = CharterTemplate(
        id=existing.id
        if existing is not None
        else storage.generate_unique_id(
            name,
            [t.id for t in saga.charter_templates] + [t.id for t in book_templates()],
        ),
        name=name,
        tribunal=tribunal,
        source=f"Saved from {covenant.name}'s charter",
        charter_name=blank(charter.name),
        preamble=blank(charter.preamble),
        probation_seasons=charter.probation_seasons,
        clauses=[
            CharterClause(c.number, blank(c.text), section=c.section)
            for c in charter.clauses
        ],
    )
    if existing is not None:
        saga.charter_templates[saga.charter_templates.index(existing)] = template
    else:
        saga.charter_templates.append(template)
    return template


def forget(saga: Saga, template_id: str) -> None:
    """Drop one of the saga's templates (the book's can't be)."""
    saga.charter_templates = [t for t in saga.charter_templates if t.id != template_id]
