"""Ancient Magic's chapters as catalog records (ancient_magic_catalog.json):
what each lost magic gives Hermetic theory, where its Insight is found, the
rolls that find it, and the Breakthroughs it suggests beyond those
rules.integrations already lists. The rules that read them are in
rules/ancient_integrations.py."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .common import known_fields

#: The three sources of Insight (DE p. 280; Ancient Magic p. 8).
INSIGHT_KINDS = ("text", "relic", "teacher")
#: The kinds of Breakthrough (DE p. 277).
BREAKTHROUGH_KINDS = ("Minor", "Major", "Hermetic")


@dataclass(frozen=True)
class InsightSource:
    """A text, relic or teacher a chapter names, what studying it gives,
    and whether it gives Insight toward the chapter's integrations."""

    name: str
    kind: str
    gives: str
    insight: bool = True
    pages: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InsightSource:
        made = cls(**known_fields(cls, data))
        if made.kind not in INSIGHT_KINDS:
            raise ValueError(
                f"Insight source {made.name!r}: kind {made.kind!r} is not one of "
                f"{INSIGHT_KINDS}"
            )
        return made


@dataclass(frozen=True)
class SearchRoll:
    """A roll the chapter sets: what it finds or does, the total rolled,
    and its Ease Factor (None when it is a level the work sets, as
    `ease_text` says)."""

    what: str
    total: str
    ease: int | None = None
    ease_text: str = ""
    pages: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SearchRoll:
        made = cls(**known_fields(cls, data))
        if made.ease is not None and not isinstance(made.ease, int):
            raise ValueError(f"Roll {made.what!r}: the Ease Factor must be a number")
        return made


@dataclass(frozen=True)
class GrigoriSecret:
    """One Secret of the Grigori (a Supernatural Virtue): the Technique and
    two Forms whose vis it makes interchangeable, and the realm that taints
    it."""

    vf_id: str
    name: str
    technique: str
    forms: tuple[str, ...] = ()
    realm: str = "Divine"

    @property
    def arts(self) -> tuple[str, ...]:
        return (self.technique, *self.forms)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GrigoriSecret:
        values = known_fields(cls, data)
        values["forms"] = tuple(values.get("forms") or ())
        made = cls(**values)
        if len(made.forms) != 2:
            raise ValueError(f"Secret {made.name!r} needs two Forms")
        return made


@dataclass(frozen=True)
class IntegrationNote:
    """What a chapter adds to one integration Breakthrough: its pages, the
    Arts and kind of effect its Insights produce, the extra point a season
    holders of certain Virtues gain, and the integration it builds on.

    With a `kind`, the note is a Breakthrough of its own that
    rules.integrations doesn't list (its target, what it gives and
    grants)."""

    name: str
    pages: str = ""
    arts: str = ""
    effect: str = ""
    #: Breakthrough points a season of research toward it, for a magus
    #: holding any of `bonus_virtues` (catalog ids).
    bonus_points: int = 0
    bonus_virtues: tuple[str, ...] = ()
    #: The integration that must be reached first (its name).
    requires: str = ""
    kind: str = ""
    target: int = 0
    gives: str = ""
    grant_kind: str = ""
    grant: str = ""
    learned: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IntegrationNote:
        values = known_fields(cls, data)
        values["bonus_virtues"] = tuple(values.get("bonus_virtues") or ())
        made = cls(**values)
        if made.kind and made.kind not in BREAKTHROUGH_KINDS:
            raise ValueError(
                f"Integration {made.name!r}: kind {made.kind!r} is not one of "
                f"{BREAKTHROUGH_KINDS}"
            )
        if made.kind and made.target <= 0:
            raise ValueError(f"Integration {made.name!r} needs a target")
        return made


@dataclass(frozen=True)
class AncientChapter:
    """One chapter of Ancient Magic: its lost magic, the tradition record
    it has (a tradition_catalog.json id, or ""), its integrations, Insight
    sources, rolls, Secrets and the numbers its rules use (`values`)."""

    id: str
    name: str
    pages: str
    source: str = "AM"
    errata: str = ""
    tradition: str = ""
    summary: str = ""
    integrations: tuple[IntegrationNote, ...] = ()
    insight_sources: tuple[InsightSource, ...] = ()
    rolls: tuple[SearchRoll, ...] = ()
    secrets: tuple[GrigoriSecret, ...] = ()
    spells: tuple[str, ...] = ()
    values: dict[str, int] = field(default_factory=dict)
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AncientChapter:
        d = known_fields(cls, data)
        d["integrations"] = tuple(
            IntegrationNote.from_dict(v) for v in d.get("integrations") or []
        )
        d["insight_sources"] = tuple(
            InsightSource.from_dict(v) for v in d.get("insight_sources") or []
        )
        d["rolls"] = tuple(SearchRoll.from_dict(v) for v in d.get("rolls") or [])
        d["secrets"] = tuple(GrigoriSecret.from_dict(v) for v in d.get("secrets") or [])
        d["spells"] = tuple(d.get("spells") or ())
        values = d.get("values") or {}
        bad = [k for k, v in values.items() if not isinstance(v, int)]
        if bad:
            raise ValueError(f"Chapter {d.get('name')!r}: values not numbers: {bad}")
        d["values"] = dict(values)
        return cls(**d)
