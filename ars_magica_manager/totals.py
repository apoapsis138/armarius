"""Registry of known modifier types, used to validate the Virtue/Flaw catalog.

A `Modifier.applies_to` (see models.py) must be a key of `MODIFIER_TYPES`.
Some modifier types vary by *which activity* is being performed -- e.g. Lab
Total differs for Inventing Spells vs. Extracting Vis, and a single Virtue
can grant a different bonus to each. Those finer-grained activities are
listed in `ACTIVITIES_BY_TYPE`, keyed by the modifier type they narrow.
A `Modifier.activity` left unset means "applies generally, regardless of
activity"; if set, it must appear in that type's activity list.

This registry is deliberately small and will grow as more of the ruleset
is modeled -- see DESIGN.md section 5.
"""

from __future__ import annotations

MODIFIER_TYPES: dict[str, str] = {
    "lab_total": "Laboratory Total, for lab activities",
    "casting_total": "Formulaic/ritual spellcasting total",
    "spontaneous_total": "Spontaneous magic total",
    "certamen_total": "Certamen total",
    "penetration_total": "Penetration total",
    "soak": "Soak total",
    "study_total": "Study total, for seasonal learning",
    "aging_roll": "Aging roll",
    "art_xp_gain": "Experience gained toward a specific Art",
    "art_score_effective": "Flat bonus to an Art's effective score, without spending xp",
    "ability_xp_gain": "Experience gained toward a specific Ability",
    "ability_score_effective": "Flat bonus to an Ability's effective score, without spending xp",
    "vis_extraction": "Vis gained from the Extract Vis lab activity",
}

ACTIVITIES_BY_TYPE: dict[str, dict[str, str]] = {
    "lab_total": {
        "invent_spells": "Invent Spells",
        "enchant_items": "Enchant Items",
        "extract_vis": "Extract Vis",
        "longevity_ritual": "Longevity Ritual",
        "original_research": "Original Research",
    },
    "study_total": {
        "reading": "Studying from a book",
        "teaching": "Being taught by another character",
        "practice": "Practising unsupervised",
    },
}


def validate_modifier_type(applies_to: str, activity: str | None) -> None:
    if applies_to not in MODIFIER_TYPES:
        raise ValueError(
            f"Unknown modifier applies_to {applies_to!r}; "
            f"must be one of {sorted(MODIFIER_TYPES)}"
        )
    if activity is None:
        return
    valid_activities = ACTIVITIES_BY_TYPE.get(applies_to, {})
    if activity not in valid_activities:
        raise ValueError(
            f"Unknown activity {activity!r} for applies_to {applies_to!r}; "
            f"must be one of {sorted(valid_activities)}"
        )
