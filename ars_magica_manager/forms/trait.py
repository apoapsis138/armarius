"""A record's Personality Traits and Reputations, independent of how they
are drawn: the form for one trait and its Add, Edit and Delete
(commands.SectionOps). A character, a familiar and a covenant share them;
a covenant's Reputations are bounded and say whether the covenant knows
of them, and every Reputation may say its kind and how far it reaches."""

from __future__ import annotations

from typing import Any

from .. import sheet_text as st
from ..commands import Form, SectionOps, delete
from ..form_spec import DialogField, attr
from ..models import ScoredTrait
from ..world import REPUTATION_TYPES

#: A covenant Reputation's least and greatest score.
COVENANT_REPUTATION_RANGE = (-3, 3)

#: Each trait list's noun and its name's example, by its section id.
NOUNS: dict[str, tuple[str, str]] = {
    "section-personality-traits": ("Personality Trait", "e.g. Brave"),
    "section-reputations": ("Reputation", "e.g. Skilled Enchanter"),
    "section-fam-personality-traits": ("Personality Trait", "e.g. Loyal"),
    "section-fam-reputations": ("Reputation", "e.g. Fierce Protector"),
    "section-cov-reputations": ("Reputation", "e.g. Feared by the local nobility"),
    "section-cr-personality-traits": ("Personality Trait", "e.g. Vain"),
    "section-cr-reputations": ("Reputation", "e.g. Haunts the ford"),
}

#: The sections whose traits are Reputations.
REPUTATION_SECTIONS = frozenset(
    section for section, (noun, _) in NOUNS.items() if noun == "Reputation"
)


def scored_trait_fields(
    name_placeholder: str,
    existing: ScoredTrait | None = None,
    *,
    min_score: int | None = None,
    max_score: int | None = None,
    include_known: bool = False,
    include_reach: bool = False,
) -> list[DialogField]:
    """A Personality Trait or Reputation: a name and a score, optionally
    bounded (covenant Reputations are -3..+3); for a Reputation, its kind
    and reach (`include_reach`) and, for a covenant's, whether the
    covenant knows of it (see inhabitants.reputation_loyalty())."""
    fields = [
        DialogField(
            "name",
            "Name",
            "text",
            attr(existing, "name", ""),
            required=True,
            placeholder=name_placeholder,
        ),
        DialogField(
            "score",
            _score_label(min_score, max_score),
            "int",
            attr(existing, "score", 0),
        ),
    ]
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
        ]
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


def _score_label(min_score: int | None, max_score: int | None) -> str:
    if min_score is None or max_score is None:
        return "Score"
    return f"Score ({min_score:+d} to {max_score:+d})"


def score_problem(
    values: dict[str, Any], min_score: int | None, max_score: int | None
) -> str | None:
    """Why a trait form's score is out of bounds, or None."""
    score = values["score"]
    if (min_score is not None and score < min_score) or (
        max_score is not None and score > max_score
    ):
        return f"Score must be between {min_score:+d} and {max_score:+d}."
    return None


def trait_from(values: dict[str, Any]) -> ScoredTrait:
    return ScoredTrait(
        name=values["name"],
        score=values["score"],
        known=values.get("known", True),
        type=values.get("type") or "",
        reach=values.get("reach", ""),
    )


def trait_ops(traits: list[ScoredTrait], section: str) -> SectionOps:
    """Add, Edit and Delete for the trait list `traits`, shown in
    `section` (one of NOUNS)."""
    noun, example = NOUNS[section]
    bounds: dict[str, Any] = {}
    if section == "section-cov-reputations":
        low, high = COVENANT_REPUTATION_RANGE
        bounds = {"min_score": low, "max_score": high, "include_known": True}
    if section in REPUTATION_SECTIONS:
        bounds["include_reach"] = True

    def form(title: str, index: int | None) -> Form:
        existing = traits[index] if index is not None else None

        def apply(values: dict[str, Any]) -> None:
            if index is None:
                traits.append(trait_from(values))
            else:
                traits[index] = trait_from(values)

        return Form(
            title,
            lambda: scored_trait_fields(example, existing, **bounds),
            apply,
            validate=lambda values: score_problem(
                values, bounds.get("min_score"), bounds.get("max_score")
            ),
        )

    return SectionOps(
        add=lambda: form(f"Add a {noun}", None),
        edit=lambda index: form(f"Edit a {noun}", index),
        remove=lambda index: delete(traits, index, traits[index].name),
        rows=lambda: [label for _, label in st.trait_rows(traits)],
    )
