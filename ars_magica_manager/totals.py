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
    "size": "A character's Size",
    "study_total": "Study total, for seasonal learning",
    "teaching_source_quality": "Source Quality of those this character teaches",
    "aging_roll": "Aging roll",
    "art_xp_gain": "Experience gained toward a specific Art",
    "art_score_effective": "Flat bonus to an Art's effective score, without spending xp",
    "ability_xp_gain": "Experience gained toward a specific Ability",
    "ability_score_effective": "Flat bonus to an Ability's effective score, without spending xp",
    "vis_extraction": "Vis gained from the Extract Vis lab activity",
    # A Laboratory Characteristic (the modifier's `target` names which one,
    # from models.LAB_CHARACTERISTICS), changed by lab Virtues and Flaws.
    "lab_characteristic": "A Laboratory Characteristic",
    # Points in a laboratory Specialization (`target` names it, or a
    # "{specialization}" the lab owner chooses from the entry's `choices`).
    "lab_specialization": "Points in a laboratory Specialization",
    # Every laboratory Specialization scoring 2 or more (Undecorated's -1).
    "lab_specialization_high": "Each laboratory Specialization scoring 2 or more",
    # Covenant scores, changed by Boons and Hooks (see DESIGN.md section 5).
    "covenant_aura": "The covenant's Magic aura",
    # A category of the covenant's yearly expenditure, in pounds.
    "covenant_expense": "Yearly expenditure",
    # A magus's Gift modifier to the covenfolk's Base Loyalty, on top of the
    # ordinary Gift's -30 (Gentle Gift +30, Blatant Gift -75).
    "gift_loyalty": "The Gift's effect on covenfolk loyalty",
    # More or fewer botch dice, for the rolls the app makes.
    "botch_dice": "Botch dice",
}

ACTIVITIES_BY_TYPE: dict[str, dict[str, str]] = {
    "casting_total": {
        "formulaic": "Formulaic spells",
        "ritual": "Ritual spells",
    },
    "lab_total": {
        "invent_spells": "Invent Spells",
        "enchant_items": "Enchant Items",
        "extract_vis": "Extract Vis",
        "longevity_ritual": "Longevity Ritual",
        "original_research": "Original Research",
        "bind_familiar": "Binding a familiar",
        "learn_from_lab_text": "Working from a Lab Text",
        # Adds to (or replaces, for the same Virtue) the activity's own.
        "experimentation": "Experimenting",
    },
    "study_total": {
        "reading": "Studying from a book",
        "teaching": "Being taught by another character",
        "practice": "Practising unsupervised",
        "training": "Being trained by a master",
        "vis_study": "Studying from raw vis",
        "adventure": "Adventure experience",
        "exposure": "Exposure experience",
    },
    "botch_dice": {
        "casting": "Casting any spell",
        "casting_words": "Casting spells with words",
        "casting_gestures": "Casting spells with gestures",
        "laboratory": "Laboratory botches (experimenting)",
    },
    # Which category of expenditure (the "activity" here is the expense line).
    "covenant_expense": {
        "buildings": "Buildings",
    },
}


def describe_modifier(
    applies_to: str,
    activity: str | None,
    amount: float | None,
    multiplier: float | None,
) -> str:
    """A modifier in words, e.g. "Yearly expenditure: Buildings +2" or
    "The covenant's Magic aura +1"."""
    what = MODIFIER_TYPES.get(applies_to, applies_to)
    if activity:
        what += f": {ACTIVITIES_BY_TYPE.get(applies_to, {}).get(activity, activity)}"
    effects = []
    if amount is not None:
        effects.append(f"{amount:+g}")
    if multiplier is not None:
        effects.append(f"x{multiplier:g}")
    return f"{what} {' '.join(effects)}".strip()


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
