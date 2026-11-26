"""A record's Personality Traits and Reputations, independent of how they
are drawn: the form for one trait and its Add, Edit and Delete
(commands.SectionOps). A character, a familiar and a covenant share them;
a covenant's Reputations are bounded and say whether the covenant knows
of them, and every Reputation may say its kind and how far it reaches."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .. import sheet_text as st
from ..commands import Form, SectionOps, delete
from ..form_spec import DialogField, attr
from ..markup import escape
from ..models import ScoredTrait
from ..models.traits import is_hubris_name
from ..rules import faerie_sympathy, reputations
from ..rules import xp as xp_rules
from ..rules.faerie_sympathy import SYMPATHY, TEMPORARY
from ..sections import LAB_TRAITS_SECTION
from ..world import REPUTATION_TYPES

#: Each trait list's noun and its name's example, by its section id.
NOUNS: dict[str, tuple[str, str]] = {
    "section-personality-traits": ("Personality Trait", "e.g. Brave"),
    "section-reputations": ("Reputation", "e.g. Skilled Enchanter"),
    "section-fam-personality-traits": ("Personality Trait", "e.g. Loyal"),
    "section-fam-reputations": ("Reputation", "e.g. Fierce Protector"),
    "section-cov-reputations": ("Reputation", "e.g. Feared by the local nobility"),
    "section-cr-personality-traits": ("Personality Trait", "e.g. Vain"),
    "section-cr-reputations": ("Reputation", "e.g. Haunts the ford"),
    LAB_TRAITS_SECTION: ("Personality Trait", "e.g. Whimsical"),
}

#: The sections whose traits are Reputations.
REPUTATION_SECTIONS = frozenset(
    section for section, (noun, _) in NOUNS.items() if noun == "Reputation"
)


#: The sections whose Personality Traits may be faerie Sympathy Traits.
SYMPATHY_SECTIONS = frozenset({"section-personality-traits"})


def scored_trait_fields(
    name_placeholder: str,
    existing: ScoredTrait | None = None,
    *,
    min_score: int | None = None,
    max_score: int | None = None,
    include_known: bool = False,
    include_reach: bool = False,
    replaceable: list[str] | None = None,
    include_sympathy: bool = False,
    include_xp: bool = False,
) -> list[DialogField]:
    """A Personality Trait or Reputation: a name and a score, optionally
    bounded (covenant Reputations are -3..+3); for a Reputation, its kind
    and reach (`include_reach`) and, for a covenant's, whether the
    covenant knows of it (see inhabitants.reputation_loyalty()); and,
    given the `replaceable` bad Reputations' names, which one it replaces
    (DE pp. 386-387); and for a character's Personality Trait, whether it
    is a faerie Sympathy Trait and whether a temporary one
    (`include_sympathy`; RoP: Faerie pp. 102-103, 127). A Personality
    Trait may gain experience (`include_xp`): its XP then stands in for its
    Score, and the score follows from it as an Ability's does."""
    fields = [
        DialogField(
            "name",
            "Name",
            "text",
            attr(existing, "name", ""),
            required=True,
            placeholder=name_placeholder,
            # Naming it Hubris makes it gain experience (DE p. 241).
            fills=_xp_fill(existing, "name") if include_xp else None,
        ),
        DialogField(
            "score",
            _score_label(min_score, max_score),
            "int",
            attr(existing, "score", 0),
            show_if=(
                (lambda values: not _xp_total(values, existing)) if include_xp else None
            ),
        ),
    ]
    if include_xp:
        fields += xp_fields(existing, sympathy=include_sympathy)
    if include_reach:
        fields += [
            DialogField(
                "type",
                "Type",
                "select",
                attr(existing, "type", "") or None,
                options=[(t, t) for t in REPUTATION_TYPES],
                allow_blank=True,
            ),
            DialogField(
                "reach",
                "Reaches",
                "text",
                attr(existing, "reach", ""),
                placeholder="e.g. the Rhine Tribunal",
            ),
            DialogField(
                "bad",
                "Bad Reputation?",
                "check",
                attr(existing, "bad", False),
                hint="A bad Reputation with its own positive score, as an Academic one "
                "is; a roll takes off the highest Bad one (A&A p. 103). Others may"
                " go below 0.",
            ),
        ]
    if replaceable:
        fields.append(
            DialogField(
                "replaces",
                "Replaces",
                "select",
                attr(existing, "replaces", "") or None,
                options=[(escape(name), name) for name in replaceable],
                allow_blank=True,
                placeholder="(no bad Reputation)",
                hint="A new Reputation started by a spectacular deed can "
                "replace a bad one: deeds that support it count toward it "
                "(DE pp. 386-387).",
            )
        )
    if include_sympathy:
        fields += sympathy_fields(existing, include_xp=include_xp)
    if include_known:
        fields.append(
            DialogField(
                "known",
                "Known by the covenant?",
                "check",
                attr(existing, "known", True),
            )
        )
    return fields


def sympathy_fields(
    existing: ScoredTrait | None, *, include_xp: bool = False
) -> list[DialogField]:
    """Whether a character's Personality Trait is a faerie Sympathy Trait,
    and whether a temporary one (RoP: Faerie pp. 102-103, 127); each box
    moves the trait between its Score and its XP when it changes whether
    it gains experience (`include_xp`)."""
    kind = attr(existing, "type", "")
    return [
        DialogField(
            "sympathy",
            "Faerie Sympathy Trait?",
            "check",
            kind in (SYMPATHY, TEMPORARY),
            hint="A bond with the Faerie realm (Winter, Iron): a fitting "
            "Ability's specialty on a stress die; rises with xp to the "
            "Warping Score, so it always gains experience; sets the "
            "Faerie Rank (RoP: Faerie pp. 102-103).",
            fills=_xp_fill(existing, "sympathy") if include_xp else None,
        ),
        DialogField(
            "temporary",
            "Temporary Sympathy Trait?",
            "check",
            kind == TEMPORARY,
            hint="From sympathetic influence or a Grant rite: works as a "
            "Sympathy Trait, but xp doesn't raise it and it isn't in the "
            "Faerie Rank (RoP: Faerie pp. 103-105, 127). A tinted aura's "
            "Traits are plain Personality Traits.",
            fills=_xp_fill(existing, "temporary") if include_xp else None,
        ),
    ]


def _score_label(min_score: int | None, max_score: int | None) -> str:
    if min_score is None or max_score is None:
        return "Score"
    return f"Score ({min_score:+d} to {max_score:+d})"


def score_problem(
    values: dict[str, Any], min_score: int | None, max_score: int | None
) -> str | None:
    """Why a trait form's score is out of bounds, or its experience can't
    be had, or None."""
    if _gains_xp(values):
        if _xp_total(values):
            xp = values.get("xp")
            return None if xp is not None and xp >= 0 else STARTS_AT_ZERO
        if not values.get("sympathy"):
            # Only a Sympathy Trait grows below 0 (RoP: Faerie p. 103).
            return STARTS_AT_ZERO
        toward = values.get("toward")
        if toward is None or toward < 0:
            return "Its XP toward the next step can't be negative."
        step = faerie_sympathy.xp_to_raise(values["score"])
        if toward >= step:
            return f"Its XP toward the next step must be under the {step} it costs."
    score = values["score"]
    if (min_score is not None and score < min_score) or (
        max_score is not None and score > max_score
    ):
        return f"Score must be between {min_score:+d} and {max_score:+d}."
    return None


#: Why a trait can't gain experience: Ability growth starts at 0.
STARTS_AT_ZERO = "A trait that gains experience starts at 0 or more."


def _by_rule(values: dict[str, Any]) -> bool:
    """Whether the rules settle that the form's Personality Trait gains
    experience, so its box isn't offered: a Sympathy Trait (lasting or
    temporary) or Hubris."""
    return bool(
        values.get("sympathy")
        or values.get("temporary")
        or (_personality(values) and is_hubris_name(values.get("name") or ""))
    )


def _personality(values: dict[str, Any]) -> bool:
    """Whether the values are a Personality Trait form's: one that can gain
    experience (a Reputation's can't)."""
    return any(key in values for key in ("gains_xp", "xp", "toward"))


def _gains_xp(values: dict[str, Any]) -> bool:
    """Whether the form's trait gains experience: a lasting Sympathy Trait
    always does (RoP: Faerie p. 103), a temporary one never (p. 127), Hubris
    always (DE p. 241), and any other when its box is ticked."""
    if values.get("temporary"):
        return False
    if values.get("sympathy"):
        return True
    if _personality(values) and is_hubris_name(values.get("name") or ""):
        return True
    return bool(values.get("gains_xp"))


def _xp_total(values: dict[str, Any], existing: ScoredTrait | None = None) -> bool:
    """Whether the form takes the trait's XP as an Ability's total: when it
    gains experience at 0 or more. Below 0, a Sympathy Trait keeps its
    Score and counts its XP toward the next step (RoP: Faerie p. 103). A
    Score not yet a number (being retyped) counts as `existing`'s, so the
    field stays where the user is typing."""
    score = values.get("score")
    if score is None and existing is not None:
        score = existing.score
    return _gains_xp(values) and not (score is not None and score < 0)


def _xp_fill(
    existing: ScoredTrait | None, box: str
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """What ticking or unticking `box` (Gains experience, Faerie Sympathy
    Trait or Temporary), or naming it Hubris (`box` "name"), fills in, when
    it moves the trait between its Score and its XP: into XP, the XP from
    the typed score (blank, and refused, for an ordinary one below 0), with
    the experience it had toward the next point if the score is the same;
    out of XP, the score its XP buys. A change that leaves it where it was
    fills nothing."""
    kept = existing.deeds if existing is not None else 0

    def fill(values: dict[str, Any]) -> dict[str, Any]:
        before = values | {box: "" if box == "name" else not values.get(box)}
        score = values.get("score")
        if _gains_xp(values) and not _gains_xp(before):
            if score is None or score < 0:
                return {} if values.get("sympathy") else {"xp": None}
            same = existing is not None and existing.score == score
            return {"xp": xp_rules.ability_xp(score) + (kept if same else 0)}
        if _xp_total(before) and not _gains_xp(values):
            xp = values.get("xp")
            if xp is None or xp < 0:
                return {}
            return {"score": xp_rules.score_from_xp(xp, xp_rules.ABILITY_FACTOR)}
        return {}

    return fill


def xp_fields(
    existing: ScoredTrait | None, *, sympathy: bool = False
) -> list[DialogField]:
    """Whether a Personality Trait gains experience, and its XP in place of
    its Score while it does: the total an Ability at its score would have,
    the experience toward the next point included. Ticking the box fills
    the XP from the typed score (blank, and refused, for one below 0);
    unticking it fills the score from the XP. With `sympathy`, the box
    gives way to the Sympathy boxes, which settle it, and a Sympathy Trait
    below 0 keeps its Score, with its XP toward the next step."""
    progress = existing.progress if existing is not None else None
    kept = existing.deeds if existing is not None else 0
    start = existing.score if existing is not None else 0
    fields = [
        DialogField(
            "gains_xp",
            "Gains experience?",
            "check",
            # One taken below 0 (a broken bargain, a punishment) opens
            # unticked, so its form can still be saved.
            existing is not None and existing.gains_xp and existing.score >= 0,
            hint="Grows from experience like an Ability, as Hubris does "
            "(DE p. 241); its XP then stands in for its Score.",
            fills=_xp_fill(existing, "gains_xp"),
            show_if=lambda values: not _by_rule(values),
        ),
        DialogField(
            "xp",
            "XP",
            "optint",
            progress.total
            if progress is not None
            else (xp_rules.ability_xp(start) + kept if start >= 0 else None),
            show_if=lambda values: _xp_total(values, existing),
        ),
    ]
    if sympathy:
        fields.append(
            DialogField(
                "toward",
                "XP toward the next step",
                "int",
                kept,
                hint="A negative Sympathy Trait rises 10 xp from -1 to 0, 15 "
                "from -2, 20 from -3 (RoP: Faerie p. 103).",
                show_if=lambda values: (
                    _gains_xp(values) and not _xp_total(values, existing)
                ),
            )
        )
    return fields


def xp_live(values: dict[str, Any]) -> str:
    """The form's live line while the trait gains experience: the score
    its XP buys and the total the next one needs."""
    if not _xp_total(values):
        return ""
    return st.live_score(values.get("xp"), xp_rules.ABILITY_FACTOR)


def trait_from(
    values: dict[str, Any], existing: ScoredTrait | None = None
) -> ScoredTrait:
    """The trait the form's values describe; an edited one keeps the deeds
    it has counted toward its next level. One that gains experience takes
    its score from its XP, the rest kept toward the next point; a Sympathy
    Trait below 0 keeps its score and its XP toward the next step."""
    bad = bool(values.get("bad"))
    deeds = existing.deeds if existing is not None else 0
    opened = existing.progress if existing is not None else None
    if _gains_xp(values) and "score" not in values:
        xp = values["xp"]
        score = xp_rules.score_from_xp(xp, xp_rules.ABILITY_FACTOR)
        deeds = xp - xp_rules.ability_xp(score)
        if existing is not None and opened is not None and xp == opened.total:
            # XP left as it opened keeps the trait as it was: a Sympathy
            # Trait held at its Warping limit banks experience past its
            # step (RoP: Faerie p. 103), which saving mustn't spend.
            score, deeds = existing.score, existing.deeds
    elif _gains_xp(values):
        score = values["score"]
        deeds = values.get("toward", 0)
    else:
        # A Reputation marked bad keeps its score's size, above 0.
        score = abs(values["score"]) if bad else values["score"]
        if (
            _personality_form(values)
            and existing is not None
            and existing.score != score
        ):
            # Experience kept while unticked belongs to the score it was
            # earned toward: a new score typed by hand starts afresh.
            deeds = 0
    return ScoredTrait(
        name=values["name"],
        score=score,
        known=values.get("known", True),
        type=_kind(values),
        reach=values.get("reach", ""),
        deeds=deeds,
        replaces=values.get("replaces") or "",
        bad=bad,
        gains_xp=_gains_xp(values),
    )


def _personality_form(values: dict[str, Any]) -> bool:
    """Whether the saved values are a Personality Trait form's, whose boxes
    may be hidden: its Gains experience box, or the Sympathy ones."""
    return _personality(values) or "sympathy" in values


def _kind(values: dict[str, Any]) -> str:
    """The trait's kind: a temporary Sympathy Trait when that box is
    ticked (it is one whether or not the first box is), a lasting one, or
    the Reputation's type."""
    if values.get("temporary"):
        return TEMPORARY
    if values.get("sympathy"):
        return SYMPATHY
    return values.get("type") or ""


def trait_ops(traits: list[ScoredTrait], section: str) -> SectionOps:
    """Add, Edit and Delete for the trait list `traits`, shown in
    `section` (one of NOUNS)."""
    noun, example = NOUNS[section]
    bounds: dict[str, Any] = {}
    if section == "section-cov-reputations":
        # Reputations have no cap (DE p. 28): a Major Prestige Boon's is 9
        # (p. 184).
        bounds = {"include_known": True}
    if section in REPUTATION_SECTIONS:
        bounds["include_reach"] = True
    if section in SYMPATHY_SECTIONS:
        bounds["include_sympathy"] = True
    if noun == "Personality Trait":
        bounds["include_xp"] = True

    def form(title: str, index: int | None) -> Form:
        existing = traits[index] if index is not None else None

        def apply(values: dict[str, Any]) -> None:
            if index is None:
                traits.append(trait_from(values))
            else:
                traits[index] = trait_from(values, existing)

        replaceable = (
            [t.name for t in traits if t is not existing and reputations.is_bad(t)]
            if section == "section-reputations"
            else None
        )
        return Form(
            title,
            lambda: scored_trait_fields(
                example, existing, replaceable=replaceable, **bounds
            ),
            apply,
            validate=lambda values: score_problem(
                values, bounds.get("min_score"), bounds.get("max_score")
            ),
            live=xp_live if bounds.get("include_xp") else None,
        )

    return SectionOps(
        add=lambda: form(f"Add a {noun}", None),
        edit=lambda index: form(f"Edit a {noun}", index),
        remove=lambda index: delete(traits, index, traits[index].name),
        rows=lambda: [label for _, label in st.trait_rows(traits)],
    )
