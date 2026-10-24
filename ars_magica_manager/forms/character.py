"""A character's Description forms, independent of how they are drawn: the
fields each asks for (form_spec.DialogField lists) and what saving one
does to the character.

Either front-end draws a form from its fields and hands the result to its
`apply`, so the terminal and the desktop edit a character the same way.
A commands.Form bundles the two as the step a sheet's Edit button runs.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from dataclasses import replace
from typing import Any

from .. import catalog, creation, faith, seasons, sourcebooks, storage
from .. import possessions as pos
from .. import sheet_text as st
from ..arts import ART_ABBREVIATIONS, ARTS, FORMS, TECHNIQUES
from ..commands import Choice, Choose, Form, SectionOps, delete, names
from ..form_spec import EMPHASIS_HINT, DialogField, covenant_options, year_born_field
from ..markup import escape, problem
from ..models import (
    COMPANION_TYPES,
    FATIGUE_LEVELS,
    FULL,
    Aging,
    ArtScore,
    Background,
    Breakthrough,
    Character,
    Characteristics,
    Description,
    HermeticBackground,
    Player,
    Possession,
    Saga,
    VirtueFlawInstance,
    Wounds,
    assign_laboratory,
    known_fields,
)
from ..rules import aging as aging_rules
from ..rules import (
    creation_characteristics,
    disease,
    experiment,
    integrations,
    medicine,
    research,
    scores,
)
from ..rules import warping as warping_rules
from ..rules import xp as xp_rules
from . import possession as possession_forms

HANDEDNESS_OPTIONS: list[tuple[str, str]] = [
    ("Right", "right"),
    ("Left", "left"),
    ("Ambidextrous", "ambidextrous"),
]

#: Biographical Detail's free-text Background fields, as (label, attribute),
#: before and after Year Born.
_BIOGRAPHY_TEXT_FIELDS: list[tuple[str, str]] = [
    ("Player", "player"),
    ("Birth Name", "birth_name"),
]
_BIOGRAPHY_TEXT_FIELDS_AFTER_YEAR: list[tuple[str, str]] = [
    ("Race/Nationality", "race_nationality"),
    ("Place of Origin", "place_of_origin"),
    ("Religion", "religion"),
    ("Title/Profession", "title_profession"),
]


def played_by_field(
    background: Background, players: Sequence[Player], may_assign: bool
) -> list[DialogField]:
    """Who plays the character, from the saga's players: only
    when the saga has players, and only the storyguide may change it."""
    if not players:
        return []
    if not may_assign:
        playing = next((p for p in players if p.id == background.player_id), None)
        return [
            DialogField(
                "_played_by",
                "Played by",
                "info",
                playing.name if playing else "(no one)",
            )
        ]
    return [
        DialogField(
            "player_id",
            "Played by",
            "select",
            background.player_id,
            options=[(escape(p.name), p.id) for p in players],
            allow_blank=True,
            placeholder="(no one)",
            hint="The player who may change this character when they sign in.",
        )
    ]


def biographical_fields(
    background: Background,
    description: Description,
    players: Sequence[Player] = (),
    *,
    may_assign: bool = True,
) -> list[DialogField]:
    """The Background fields not in the top panel, then every Description
    field."""
    d = description
    return [
        *(
            DialogField(attribute, label, "text", getattr(background, attribute))
            for label, attribute in _BIOGRAPHY_TEXT_FIELDS
        ),
        *played_by_field(background, players, may_assign),
        year_born_field(background.year_born),
        *(
            DialogField(attribute, label, "text", getattr(background, attribute))
            for label, attribute in _BIOGRAPHY_TEXT_FIELDS_AFTER_YEAR
        ),
        DialogField("height", "Height", "optfloat", d.height),
        DialogField("weight", "Weight", "optfloat", d.weight),
        DialogField("hair", "Hair", "text", d.hair),
        DialogField("eyes", "Eyes", "text", d.eyes),
        DialogField(
            "handedness",
            "Handedness",
            "select",
            d.handedness,
            options=HANDEDNESS_OPTIONS,
        ),
        DialogField(
            "physical_description",
            "Physical Description",
            "text",
            d.physical_description,
        ),
        DialogField("biography", "Biography", "area", d.biography, hint=EMPHASIS_HINT),
    ]


def apply_biographical(character: Character, result: dict[str, Any]) -> None:
    for attribute in known_fields(Background, result):
        setattr(character.background, attribute, result[attribute])
    character.description = Description(**known_fields(Description, result))


def aging_fields(aging: Aging, saga: Saga | None = None) -> list[DialogField]:
    """The Aging & Warping form; with Art & Academe in play, a physician's
    regimen too."""
    return [
        DialogField("decrepitude", "Decrepitude", "int", aging.decrepitude),
        DialogField("effects", "Effects of Aging", "text", aging.effects),
        DialogField("warping_score", "Warping Score", "int", aging.warping_score),
        DialogField("warping_points", "Warping Points", "int", aging.warping_points),
        DialogField(
            "aura_time",
            "Time in their home aura",
            "select",
            aging.aura_time or warping_rules.ALWAYS,
            options=[(label, key) for key, label in warping_rules.AURA_TIMES.items()],
            hint="Sets the yearly Warping from a strong aura (DE p. 390).",
        ),
        DialogField(
            "gain_warping",
            "Gain Warping Points now",
            "int",
            0,
            hint="From one event (a powerful effect, a botch...): 2 or more "
            "take a magus to the edge of Wizard's Twilight, rolled at once.",
        ),
        DialogField(
            "warping_aura",
            "Aura where it happened",
            "optint",
            None,
            show_if=lambda v: (v.get("gain_warping") or 0) >= 2,
            hint="Blank: the aura where they live (DE p. 228).",
        ),
        DialogField(
            "enter_twilight",
            "Enter Twilight willingly",
            "check",
            False,
            show_if=lambda v: (v.get("gain_warping") or 0) >= 2,
            hint="No roll to avoid it (DE p. 228).",
        ),
        *_regimen_fields(aging, saga),
    ]


def _regimen_fields(aging: Aging, saga: Saga | None) -> list[DialogField]:
    if saga is None or not sourcebooks.in_play("A&A", sourcebooks.saga_books(saga)):
        return []
    physicians = [c for c in saga.characters if medicine.medicine(c) > 0]
    if not physicians and not aging.regimen:
        return []
    return [
        DialogField(
            "regimen",
            "Regimen",
            "select",
            str(aging.regimen),
            options=[
                ("None", "0"),
                ("+1 (Medicine 1; up to Medicine x 5 clients)", "1"),
                ("+2 (Medicine 4; up to Medicine clients)", "2"),
                ("+3 (Medicine 7; a single client)", "3"),
            ],
            hint="A physician's diet and bloodletting: its bonus to Living "
            "Conditions for aging, once lived under for a year.",
        ),
        DialogField(
            "regimen_by",
            "Its physician",
            "select",
            aging.regimen_by or None,
            options=[(escape(c.name), c.id) for c in physicians],
            allow_blank=True,
        ),
        DialogField("regimen_since", "Begun in (year)", "optint", aging.regimen_since),
    ]


def apply_aging(
    saga: Saga,
    character: Character,
    result: dict[str, Any],
    rng: random.Random | None = None,
) -> list[str]:
    """Save the Aging & Warping form; the notes Warping gained now gives
    (a Twilight episode rolled at once)."""
    result = dict(result)
    gained = result.pop("gain_warping", 0) or 0
    aura = result.pop("warping_aura", None)
    enter = bool(result.pop("enter_twilight", False))
    if "regimen" in result:
        result["regimen"] = int(result["regimen"] or 0)
        result["regimen_by"] = result.get("regimen_by") or ""
    aging = character.aging
    if result["decrepitude"] != aging.decrepitude:
        aging.decrepitude_points = aging_rules.points_for_score(result["decrepitude"])
    # Only the fields on the form: the rest (Longevity, Aging Points) stays.
    for key, value in result.items():
        setattr(aging, key, value)
    if gained > 0:
        return seasons.gain_warping(
            saga, character, gained, rng or random.Random(), aura=aura, enter=enter
        )
    return []


def wounds_fields(
    wounds: Wounds, *, soak: bool = True, academe: bool = False
) -> list[DialogField]:
    """Wound counts and Incapacitated/Dead; a character's Soak too (a
    Familiar's lives with its Characteristics instead); with Art & Academe's
    medicine, the Recovery Modifiers of where the patient heals and a
    disease cured by other means."""
    fields = (
        [
            DialogField(
                "soak",
                "Soak adjustment",
                "int",
                wounds.soak,
                hint="Added to the Soak worked out from Stamina, armour and Virtues.",
            )
        ]
        if soak
        else []
    )
    return fields + [
        DialogField("light", "Light Wounds (-1 each)", "int", wounds.light),
        DialogField("medium", "Medium Wounds (-3 each)", "int", wounds.medium),
        DialogField("heavy", "Heavy Wounds (-5 each)", "int", wounds.heavy),
        DialogField("incapacitated", "Incapacitated", "check", wounds.incapacitated),
        DialogField("dead", "Dead", "check", wounds.dead),
        *(academe_fields(wounds) if academe else []),
    ]


def academe_fields(wounds: Wounds) -> list[DialogField]:
    return [
        *(
            DialogField(
                f"condition_{key}",
                f"{label} ({amount:+d})",
                "check",
                key in wounds.conditions,
            )
            for key, (label, amount) in disease.CONDITIONS.items()
        ),
        *(
            DialogField(
                f"cured_{index}",
                f"{escape(d.name)} cured",
                "check",
                False,
                hint="By magic, a saint or a surgeon: it goes.",
            )
            for index, d in enumerate(wounds.diseases)
        ),
    ]


def apply_wounds(wounds: Wounds, result: dict[str, Any]) -> Wounds:
    """Wounds as the Edit Wounds form leaves them."""
    found = dict(result)
    conditions = [
        key for key in disease.CONDITIONS if found.pop(f"condition_{key}", False)
    ]
    cured = {i for i in range(len(wounds.diseases)) if found.pop(f"cured_{i}", False)}
    updated = wounds.with_counts(**found)
    if any(f"condition_{key}" in result for key in disease.CONDITIONS):
        updated.conditions = conditions
        updated.diseases = [d for i, d in enumerate(wounds.diseases) if i not in cured]
    return updated


def fatigue_fields(level: str) -> list[DialogField]:
    return [
        DialogField(
            "level",
            "Level",
            "select",
            level,
            options=[(level.title(), level) for level in FATIGUE_LEVELS],
        )
    ]


def hermetic_fields(hermetic: HermeticBackground) -> list[DialogField]:
    h = hermetic
    return [
        DialogField(
            "house",
            "House",
            "select",
            h.house,
            options=[(house.name, house.id) for house in catalog.load_house_catalog()],
            allow_blank=True,
            placeholder="(none selected)",
        ),
        DialogField("domus_magna", "Domus Magna", "text", h.domus_magna),
        DialogField("primus", "Primus", "text", h.primus),
        DialogField("parens", "Parens", "text", h.parens),
        DialogField(
            "covenant_of_apprenticeship",
            "Covenant of Apprenticeship",
            "text",
            h.covenant_of_apprenticeship,
        ),
        DialogField(
            "age_of_apprenticeship",
            "Age of Apprenticeship",
            "optint",
            h.age_of_apprenticeship,
        ),
        DialogField("wizards_sigil", "Wizard's Sigil", "area", h.wizards_sigil),
    ]


def description_edits(
    saga: Saga, character: Character, *, may_assign: bool = True
) -> dict[str, Form]:
    """The Description chapter's Edit buttons, by the section they edit."""
    c = character

    def set_wounds(result: dict[str, Any]) -> None:
        c.wounds = apply_wounds(c.wounds, result)

    def set_fatigue(result: dict[str, Any]) -> None:
        c.fatigue_level = result["level"]

    def set_hermetic(result: dict[str, Any]) -> None:
        c.hermetic = HermeticBackground(**result)

    edits = {
        "Biographical Detail": Form(
            "Edit Biographical Detail",
            lambda: biographical_fields(
                c.background, c.description, saga.players, may_assign=may_assign
            ),
            lambda result: apply_biographical(c, result),
        ),
        "Wounds": Form(
            "Edit Wounds",
            lambda: wounds_fields(
                c.wounds, academe=disease.on(saga) or bool(c.wounds.diseases)
            ),
            set_wounds,
        ),
        "Fatigue": Form(
            "Edit Fatigue Level",
            lambda: fatigue_fields(c.fatigue_level),
            set_fatigue,
        ),
        "Aging": Form(
            "Edit Aging & Warping",
            lambda: aging_fields(c.aging, saga),
            lambda result: apply_aging(saga, c, result),
        ),
    }
    if c.type == "magus":
        edits["Hermetic Background"] = Form(
            "Edit Hermetic Background",
            lambda: hermetic_fields(c.hermetic),
            set_hermetic,
        )
    return edits


# -- the header: Character Info and Characteristics --

#: The eight Characteristics as (label, attribute), in the book's order.
CHARACTERISTIC_FIELDS: list[tuple[str, str]] = [
    ("Intelligence (Int)", "intelligence"),
    ("Perception (Per)", "perception"),
    ("Presence (Pre)", "presence"),
    ("Communication (Com)", "communication"),
    ("Strength (Str)", "strength"),
    ("Stamina (Sta)", "stamina"),
    ("Dexterity (Dex)", "dexterity"),
    ("Quickness (Qik)", "quickness"),
]

#: The types a companion may be changed between, as select options.
COMPANION_TYPE_OPTIONS: list[tuple[str, str]] = [
    ("Companion", "companion"),
    ("Mythic Companion", "mythic companion"),
]


def characteristics_fields(characteristics: Characteristics) -> list[DialogField]:
    return [
        DialogField(attribute, label, "int", getattr(characteristics, attribute))
        for label, attribute in CHARACTERISTIC_FIELDS
    ]


def characteristics_from(values: dict[str, Any]) -> Characteristics:
    return Characteristics(
        **{attribute: values[attribute] for _, attribute in CHARACTERISTIC_FIELDS}
    )


def characteristics_live(
    saga: Saga, character: Character
) -> Callable[[dict[str, Any]], str] | None:
    """While the character is In Creation, the points spent and left as
    each score is typed; otherwise no live line."""
    if not character.in_creation:
        return None
    return lambda values: creation_characteristics.points_text(saga, character, values)


def characteristics_form(saga: Saga, character: Character) -> Form:
    def apply(values: dict[str, Any]) -> None:
        character.characteristics = characteristics_from(values)

    return Form(
        "Edit Characteristics",
        lambda: characteristics_fields(character.characteristics),
        apply,
        live=characteristics_live(saga, character),
    )


def character_info_fields(saga: Saga, character: Character) -> list[DialogField]:
    """The top panel's Edit form: name, a companion's type (Companion or
    Mythic Companion), covenant, a magus's laboratory, and the Background
    figures shown there."""
    b = character.background
    fields = [
        DialogField("name", "Name", "text", character.name, required=True),
    ]
    if character.detail != FULL:
        # A Line or Sketch character has no Biography: this says who they are.
        fields.append(
            DialogField(
                "summary",
                "In the Saga",
                "area",
                character.summary,
                placeholder="Who they are and what they want, in a sentence or two",
            )
        )
    if character.type in COMPANION_TYPES:
        fields.append(
            DialogField(
                "type",
                "Type",
                "select",
                character.type,
                options=COMPANION_TYPE_OPTIONS,
            )
        )
    fields.append(
        DialogField(
            "covenant_id",
            "Covenant",
            "select",
            character.covenant_id,
            options=covenant_options(saga),
            allow_blank=True,
            placeholder="(unassigned)",
        )
    )
    if character.type == "magus":
        fields.append(
            DialogField(
                "laboratory_id",
                "Assigned Laboratory",
                "select",
                character.assigned_lab_id,
                options=[(escape(lab.name), lab.id) for lab in saga.laboratories],
                allow_blank=True,
                placeholder="(unassigned)",
            )
        )
    return fields + [
        DialogField("setting", "Setting", "text", b.setting),
        DialogField("confidence_score", "Confidence Score", "int", b.confidence_score),
        DialogField(
            "confidence_points", "Confidence Points", "int", b.confidence_points
        ),
        DialogField(
            "true_faith_score",
            "True Faith Score",
            "int",
            b.true_faith_score,
            hint="Only with the True Faith Virtue; 2+ is a Mythic Companion.",
        ),
        DialogField("faith_points", "Faith Points", "int", b.faith_points),
        DialogField("size", "Size", "int", b.size),
        DialogField(
            "silver",
            "Silver (pounds)",
            "int",
            character.silver,
            hint="What they carry, counted as a covenant's Wealth is. Give "
            "moves it to another character or a covenant.",
        ),
    ]


def character_info_live(character: Character) -> Callable[[dict[str, Any]], str]:
    """Warns (not refuses) as the True Faith Score is typed if the
    character can't have it (faith.faith_warnings)."""

    def live(values: dict[str, Any]) -> str:
        score = values.get("true_faith_score") or 0
        kind = values.get("type") or character.type
        warnings = faith.faith_warnings(character, score, kind)
        return "\n".join(problem(escape(w)) for w in warnings)

    return live


def apply_character_info(
    saga: Saga, character: Character, result: dict[str, Any]
) -> None:
    character.name = result["name"]
    character.summary = result.get("summary", character.summary)
    character.type = result.get("type", character.type)
    character.covenant_id = result["covenant_id"]
    if character.type == "magus":
        assign_laboratory(saga, character, result["laboratory_id"])
    background = character.background
    for key in (
        "setting",
        "confidence_score",
        "confidence_points",
        "true_faith_score",
        "faith_points",
        "size",
    ):
        setattr(background, key, result[key])
    character.silver = max(0, result.get("silver", character.silver) or 0)


def character_info_form(saga: Saga, character: Character) -> Form:
    return Form(
        "Edit Character Info",
        lambda: character_info_fields(saga, character),
        lambda result: apply_character_info(saga, character, result),
        live=character_info_live(character),
    )


# -- the Arts --


def arts_fields(arts: dict[str, ArtScore]) -> list[DialogField]:
    """Every Art's total xp, the Techniques then the Forms."""
    return [
        DialogField(
            f"art_{art.lower()}",
            f"{art} ({ART_ABBREVIATIONS[art]}) XP",
            "int",
            arts.get(art.lower(), ArtScore()).xp,
        )
        for art in ARTS
    ]


def arts_problem(values: dict[str, Any]) -> str | None:
    for art in ARTS:
        if values[f"art_{art.lower()}"] < 0:
            return f"{art}'s XP can't be negative."
    return None


def art_bonuses(virtues_flaws: Sequence[VirtueFlawInstance]) -> dict[str, int]:
    """Each Art's fixed bonus (Puissant), by the Art's name."""
    return {art: scores.art_bonus(virtues_flaws, art)[0] for art in ARTS}


def art_score(xp: int | None, bonus: int) -> tuple[str, int] | None:
    """An Art's score as a list shows it ("10 (13)" with a `bonus`) and the
    total xp its next score needs, or None while `xp` isn't a number."""
    if xp is None or xp < 0:
        return None
    progress = xp_rules.progress(xp, xp_rules.ART_FACTOR)
    return st.adjusted_score(progress.score, bonus), progress.next_total


def arts_live(
    virtues_flaws: Sequence[VirtueFlawInstance], note: str = ""
) -> Callable[[dict[str, Any]], str]:
    """Each Art's score (with the owner's Puissant) and the total xp its
    next score needs, kept up to date as the xp is typed; `note` after
    them (e.g. how much xp the Creation Worksheet gave the Arts)."""
    bonus = art_bonuses(virtues_flaws)

    def score(art: str, xp: int | None) -> str:
        found = art_score(xp, bonus[art])
        if found is None:
            return f"{ART_ABBREVIATIONS[art]} ?"
        shown, next_total = found
        return f"{ART_ABBREVIATIONS[art]} {shown} (next at {next_total})"

    def live(values: dict[str, Any]) -> str:
        lines = [
            "  ".join(score(art, values.get(f"art_{art.lower()}")) for art in arts)
            for arts in (TECHNIQUES, FORMS)
        ]
        if note:
            lines.append(f"[$text-warning]{escape(note)}[/]")
        return "\n".join(lines)

    return live


def arts_form(character: Character) -> Form:
    def apply(values: dict[str, Any]) -> None:
        character.arts = {
            art.lower(): ArtScore(xp=values[f"art_{art.lower()}"]) for art in ARTS
        }

    return Form(
        "Edit Arts",
        lambda: arts_fields(character.arts),
        apply,
        validate=arts_problem,
        live=arts_live(
            character.virtues_flaws, creation.worksheet_note(character, ARTS)
        ),
    )


# -- Research Goals --

#: What reaching a research goal grants (Breakthrough.grant_kind).
GRANT_KINDS = [
    ("An Ability (the points become its xp)", "Ability"),
    ("A Virtue", "Virtue"),
    ("A new Range, Duration or Target", "Parameter"),
]


def research_goal_options(character: Character) -> list[tuple[str, str]]:
    """Select options for a season's research goal: the magus's goals not
    yet reached, each with its kind and where it stands."""
    return [
        (f"{escape(goal.name)} ({goal.kind}): {research.stage(goal).value}", goal.name)
        for goal in character.breakthroughs
        if not goal.reached
    ]


def research_goal_fields(existing: Breakthrough | None) -> list[DialogField]:
    """A magus's Arcane Discovery goal: what it is, the kind of
    Breakthrough sought (Minor, Major, Hermetic; its target follows, and
    the storyguide may type a secret one), and what reaching it grants."""
    virtues = sorted(
        (d for d in catalog.load_virtue_flaw_catalog() if d.type == "Virtue"),
        key=lambda d: d.name,
    )
    grant_kind = existing.grant_kind if existing else ""

    def grant(kind: str) -> str:
        return existing.grant if existing and grant_kind == kind else ""

    def kind_target(values: dict[str, Any]) -> dict[str, Any]:
        kind = values.get("kind") or ""
        known = integrations.BY_NAME.get(values.get("known") or "")
        if known is not None and known.kind == kind:
            return {"target": known.target}
        return {"target": experiment.KINDS.get(kind, 30)}

    known = (
        []
        if existing
        else [
            DialogField(
                "known",
                "Integration",
                "select",
                None,
                options=[(escape(i.label), i.name) for i in integrations.INTEGRATIONS],
                allow_blank=True,
                placeholder="(a goal of your own)",
                hint="A breakthrough the books name; it fills in the rest.",
                fills=_integration_fill,
            )
        ]
    )
    return [
        *known,
        DialogField(
            "name",
            "Goal",
            "text",
            existing.name if existing else "",
            required=True,
            placeholder="e.g. Penetrating the Aegis",
        ),
        DialogField(
            "description",
            "What it is",
            "area",
            existing.description if existing else "",
        ),
        DialogField(
            "kind",
            "Breakthrough",
            "select",
            existing.kind if existing else "Minor",
            options=[
                (f"{kind} ({points} points)", kind)
                for kind, points in experiment.KINDS.items()
            ],
            required=True,
            fills=kind_target,
        ),
        DialogField(
            "target",
            "Target",
            "int",
            existing.target if existing else experiment.KINDS["Minor"],
            hint="The storyguide may set a secret target.",
        ),
        DialogField(
            "hidden_target",
            "Keep the target secret",
            "check",
            existing.hidden_target if existing else False,
            hint="The sheet then shows the points gained, not how many are "
            "needed (DE recommends the player not know).",
        ),
        DialogField(
            "points", "Points so far", "int", existing.points if existing else 0
        ),
        DialogField(
            "grant_kind",
            "Reaching it grants",
            "select",
            grant_kind or None,
            options=GRANT_KINDS,
            allow_blank=True,
            placeholder="(the troupe decides)",
        ),
        DialogField(
            "grant_ability",
            "Ability",
            "text",
            grant("Ability"),
            show_if=lambda values: values.get("grant_kind") == "Ability",
        ),
        DialogField(
            "grant_virtue",
            "Virtue",
            "select",
            grant("Virtue") or None,
            options=[(escape(d.name), d.id) for d in virtues],
            allow_blank=True,
            show_if=lambda values: values.get("grant_kind") == "Virtue",
        ),
        DialogField(
            "grant_parameter",
            "Parameter",
            "text",
            grant("Parameter"),
            placeholder="e.g. Range: Horizon (as Sight)",
            hint="Range, Duration or Target, its name, and the standard one it "
            "costs as (+n for more); one the app knows needs only its name.",
            show_if=lambda values: values.get("grant_kind") == "Parameter",
        ),
    ]


def _integration_fill(values: dict[str, Any]) -> dict[str, Any]:
    """What a named integration breakthrough fills in."""
    known = integrations.BY_NAME.get(values.get("known") or "")
    if known is None:
        return {}
    filled: dict[str, Any] = {
        "name": known.name,
        "description": f"{known.gives} ({known.book})",
        "kind": known.kind,
        "target": known.target,
        "grant_kind": known.grant_kind or None,
    }
    if known.grant_kind:
        filled[f"grant_{known.grant_kind.lower()}"] = known.grant
    return filled


def research_goal_from(
    existing: Breakthrough | None, values: dict[str, Any]
) -> Breakthrough:
    """The goal the form describes (a copy of `existing`, keeping what the
    form doesn't show); a goal whose target rose above its points is no
    longer reached."""
    kind = values.get("grant_kind") or ""
    made = replace(existing) if existing else Breakthrough(name="")
    made.name = values["name"]
    made.description = values.get("description") or ""
    made.kind = values["kind"]
    made.target = values["target"]
    made.points = values.get("points") or 0
    made.hidden_target = bool(values.get("hidden_target"))
    made.grant_kind = kind
    made.grant = (values.get(f"grant_{kind.lower()}") or "") if kind else ""
    made.reached = made.reached and made.points >= made.target
    return made


def research_goal_problem(values: dict[str, Any]) -> str | None:
    if (values.get("target") or 0) < 1:
        return "The target is at least 1 point."
    if (values.get("points") or 0) < 0:
        return "The points gained can't be negative."
    return None


def research_goal_ops(character: Character) -> SectionOps:
    """Add, Edit and Delete for the magus's Research Goals."""
    goals = character.breakthroughs

    def form(index: int | None) -> Form:
        existing = goals[index] if index is not None else None

        def apply(values: dict[str, Any]) -> None:
            goal = research_goal_from(existing, values)
            if index is None:
                goals.append(goal)
            else:
                goals[index] = goal

        return Form(
            "Add Research Goal" if index is None else "Edit Research Goal",
            lambda: research_goal_fields(existing),
            apply,
            validate=research_goal_problem,
            save_label="Add" if index is None else "Save",
        )

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=lambda index: delete(goals, index, goals[index].name),
        rows=names(goals),
    )


# -- Personal Gear --

#: The kinds of item a character carries, as Add's first question offers
#: them.
INVENTORY_KINDS: list[tuple[str, str]] = [
    ("Weapon", "weapon"),
    ("Armor", "armor"),
    ("Item", "item"),
]


def inventory_ops(character: Character) -> SectionOps:
    """Add (which kind first: the section is one combined list, unlike
    the covenant's per-kind sections), Edit and Delete for Personal
    Gear."""
    inventory = character.inventory

    def form(kind: str, index: int | None) -> Form:
        existing = inventory[index] if index is not None else None
        entry = pos.PossessionEntry(kind, existing) if existing is not None else None
        title = (
            f"Add a {pos.KIND_SINGULAR[kind]}"
            if existing is None
            else f"Edit {escape(existing.name or 'this item')}"
        )

        def apply(values: dict[str, Any]) -> None:
            if existing is not None:
                for key, value in values.items():
                    setattr(existing, key, value)
                return
            inventory.append(
                Possession(
                    id=storage.generate_unique_id(
                        values.get("name") or kind, [item.id for item in inventory]
                    ),
                    kind=kind,
                    **values,
                )
            )

        return possession_forms.possession_form(title, kind, entry, apply)

    return SectionOps(
        add=lambda: Choose(
            "Add which kind of item?",
            lambda: [Choice(label, kind) for label, kind in INVENTORY_KINDS],
            lambda kind: form(kind, None),
        ),
        edit=lambda index: form(inventory[index].kind, index),
        remove=lambda index: delete(
            inventory, index, inventory[index].name or "this item"
        ),
        rows=lambda: [
            pos.row_label(pos.PossessionEntry(item.kind, item)) for item in inventory
        ],
    )
