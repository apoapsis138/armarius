"""Spell levels from their design: a guideline's base level
plus a magnitude per Range, Duration and Target step, plus any size and
requisite magnitudes.

| + magnitudes | Range             | Duration                 | Target                  |
|--------------|-------------------|--------------------------|-------------------------|
| 0            | Personal          | Momentary                | Individual, Circle, Taste |
| 1            | Touch, Eye        | Concentration, Diameter  | Part, Touch (sense)     |
| 2            | Voice             | Sun, Ring                | Group, Room, Smell      |
| 3            | Sight             | Moon                     | Structure, Hearing      |
| 4            | Arcane Connection | Year                     | Boundary, Vision        |

A magnitude is 5 levels, except below level 5, where it is 1 level. A spell
must be a Ritual with Year Duration, Boundary Target or a level over 50, and
a Ritual is always at least level 20.

No screen uses extra_parameters() yet: it is a rule for a screen still to
come, and only the tests call it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Nine: Spells, Changing Ranges, "
    "Durations, and Targets "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Nine:"
    "_Spells#Changing_Ranges,_Durations,_and_Targets)"
)

RANGE_STEPS: dict[str, int] = {
    "Personal": 0,
    "Touch": 1,
    "Eye": 1,
    "Voice": 2,
    "Sight": 3,
    "Arcane Connection": 4,
}
DURATION_STEPS: dict[str, int] = {
    "Momentary": 0,
    "Concentration": 1,
    "Diameter": 1,
    "Sun": 2,
    "Ring": 2,
    "Moon": 3,
    "Year": 4,
}
TARGET_STEPS: dict[str, int] = {
    "Individual": 0,
    "Circle": 0,
    "Taste": 0,
    "Part": 1,
    "Touch": 1,
    "Group": 2,
    "Room": 2,
    "Smell": 2,
    "Structure": 3,
    "Hearing": 3,
    "Boundary": 4,
    "Vision": 4,
}


@dataclass(frozen=True)
class ExtraParameter:
    """A Range, Duration or Target beyond the standard ones, which a Virtue,
    Mystery or breakthrough grants (reference/spell-parameters.md): it costs
    the same magnitudes as a standard parameter, plus any it adds."""

    kind: str  # "range", "duration" or "target"
    name: str
    costs_as: str
    #: The character Virtue/Flaw catalog ids that grant it.
    granted_by: tuple[str, ...]
    #: Whether a spell with it must be a Ritual.
    ritual: bool = False
    #: Extra magnitudes on top of what it costs as (If (Condition): +4).
    plus: int = 0
    #: The name a breakthrough grants it under, when that grants several
    #: (Event, whatever the triggered effect's own Duration).
    family: str = ""

    @property
    def label(self) -> str:
        """Its name and what it costs, as a select lists it."""
        more = f" +{self.plus}" if self.plus else ""
        return f"{self.name} (as {self.costs_as}{more})"


EXTRA_PARAMETERS: tuple[ExtraParameter, ...] = (
    ExtraParameter(
        "duration", "Performance", "Concentration", ("vf_performance_magic",)
    ),
    ExtraParameter("range", "Adelphixis", "Arcane Connection", ("vf_orphic_magic",)),
    ExtraParameter("duration", "Held", "Concentration", ("vf_spell_timing",)),
    ExtraParameter("duration", "Midday/Midnight", "Sun", ("vf_spell_timing",)),
    ExtraParameter("duration", "Season", "Moon", ("vf_spell_timing",), ritual=True),
    ExtraParameter(
        "duration", "While (Condition)", "Concentration", ("vf_spell_timing",)
    ),
    ExtraParameter("duration", "Not (Condition)", "Sun", ("vf_spell_timing",)),
    ExtraParameter("duration", "Might", "Year", ("vf_perpetuity",), ritual=True),
    ExtraParameter("duration", "Aura", "Year", ("vf_perpetuity",), ritual=True),
    ExtraParameter("duration", "Hidden", "Year", ("vf_perpetuity",), ritual=True),
    ExtraParameter("duration", "Minutes", "Diameter", ("vf_celestial_magic",)),
    ExtraParameter("duration", "Hours", "Sun", ("vf_celestial_magic",)),
    ExtraParameter("duration", "Days", "Moon", ("vf_celestial_magic",)),
    ExtraParameter("duration", "Signs", "Year", ("vf_celestial_magic",), ritual=True),
    ExtraParameter("range", "Line", "Sight", ("vf_hermetic_geometry",)),
    ExtraParameter("target", "Arcane Circle", "Part", ("vf_hermetic_geometry",)),
    ExtraParameter("duration", "Arcane Ring", "Moon", ("vf_hermetic_geometry",)),
    ExtraParameter("range", "Road", "Voice", ("vf_road_magic", "vf_mercurian_magic")),
    ExtraParameter(
        "range",
        "Road Network",
        "Arcane Connection",
        ("vf_road_magic", "vf_mercurian_magic"),
        ritual=True,
    ),
    ExtraParameter("target", "Road", "Room", ("vf_road_magic", "vf_mercurian_magic")),
    ExtraParameter(
        "target",
        "Road Network",
        "Boundary",
        ("vf_road_magic", "vf_mercurian_magic"),
        ritual=True,
    ),
    ExtraParameter("target", "Flavor", "Individual", ("vf_sensory_magic",)),
    ExtraParameter("target", "Texture", "Part", ("vf_sensory_magic",)),
    ExtraParameter("target", "Scent", "Group", ("vf_sensory_magic",)),
    ExtraParameter("target", "Sound", "Structure", ("vf_sensory_magic",)),
    # Ancient Magic. Those granted by no Virtue come from a breakthrough
    # (spell_parameters), or from knowing a spell that uses one.
    ExtraParameter("range", "Veil of Death", "Sight", ("vf_canaanite_magic",)),
    ExtraParameter("range", "Unlimited", "Arcane Connection", (), ritual=True, plus=2),
    *(
        ExtraParameter(
            "duration",
            f"Event ({short})",
            then,
            (),
            ritual=True,
            plus=1,
            family="Event",
        )
        for short, then in (
            ("Mom", "Momentary"),
            ("Diam", "Diameter"),
            ("Sun", "Sun"),
            ("Moon", "Moon"),
            ("Year", "Year"),
        )
    ),
    ExtraParameter("duration", "19 Years", "Year", (), ritual=True, plus=1),
    ExtraParameter(
        "target", "Unborn Child", "Individual", ("vf_fertility_ritual_magic",)
    ),
    ExtraParameter("duration", "Rune", "Moon", ("vf_hermetic_rune_magic",)),
    ExtraParameter("target", "Inscription", "Individual", ("vf_hermetic_rune_magic",)),
)

_STANDARD: dict[str, dict[str, int]] = {}  # filled below


def extra_parameters(kind: str, vf_ids: set[str]) -> list[ExtraParameter]:
    """The extra `kind` parameters a magus with these Virtue/Flaw ids may
    use."""
    return [
        e
        for e in EXTRA_PARAMETERS
        if e.kind == kind and any(v in vf_ids for v in e.granted_by)
    ]


def extra(kind: str, name: str) -> ExtraParameter | None:
    """The extra parameter of this kind and name, if the app knows it."""
    return next(
        (e for e in EXTRA_PARAMETERS if e.kind == kind and e.name == name), None
    )


def steps_of(kind: str, name: str) -> int | None:
    """The magnitudes a Range/Duration/Target costs, standard or extra
    (None for one the app doesn't know)."""
    standard = _STANDARD[kind]
    if name in standard:
        return standard[name]
    found = extra(kind, name)
    if found is None:
        return None
    return standard[found.costs_as] + found.plus


def needs_ritual(kind: str, name: str) -> bool:
    """Whether a parameter makes a spell a Ritual."""
    if (kind, name) in (("duration", "Year"), ("target", "Boundary")):
        return True
    return any(e.ritual for e in EXTRA_PARAMETERS if e.kind == kind and e.name == name)


RITUAL_MINIMUM = 20
MAX_NON_RITUAL = 50


def add_magnitudes(level: int, magnitudes: int) -> int:
    """`level` raised (or, for a negative count, lowered) by magnitudes: 5
    levels each, 1 below level 5 (15 less 5 magnitudes is 2)."""
    for _ in range(magnitudes):
        level = level + 1 if level < 5 else level + 5
    for _ in range(-magnitudes):
        level = level - 1 if level <= 5 else level - 5
    return max(level, 1)


@dataclass
class Design:
    """A spell level worked out from its design."""

    level: int
    #: (what, magnitudes) for each step, as a stat block's design line lists.
    steps: list[tuple[str, int]] = field(default_factory=list)
    ritual_required: bool = False
    #: Why it must be a Ritual, or why the level was raised.
    notes: list[str] = field(default_factory=list)

    def design_line(self, base: int) -> str:
        """The stat block's design line: "Base 5, +2 Voice, +2 Sun, +2 Group"."""
        return ", ".join(
            [f"Base {base}", *(f"{n:+d} {what}" for what, n in self.steps)]
        )


def spell_level(
    base: int,
    range_: str,
    duration: str,
    target: str,
    *,
    extra_magnitudes: int = 0,
    ritual: bool = False,
    custom_steps: dict[str, int] | None = None,
) -> Design | None:
    """The level of a spell with this base and Range/Duration/Target, plus
    `extra_magnitudes` of size and requisites. A parameter a Virtue or
    Mystery grants costs as its standard counterpart; `custom_steps` gives
    the magnitudes of any other ("range"/"duration"/"target" -> n: a
    breakthrough or a troupe ruling). None when a parameter is unknown."""
    custom = custom_steps or {}
    steps = []
    for kind, name in (("range", range_), ("duration", duration), ("target", target)):
        count = custom.get(kind, steps_of(kind, name))
        if count is None:
            return None
        steps.append((name, count))
    if extra_magnitudes:
        steps.append(("size/requisites", extra_magnitudes))
    level = add_magnitudes(base, sum(n for _, n in steps))
    design = Design(level=level, steps=steps)
    for kind, name in (("range", range_), ("duration", duration), ("target", target)):
        if needs_ritual(kind, name):
            design.notes.append(f"{name} {kind.title()} needs a Ritual.")
    if level > MAX_NON_RITUAL:
        design.notes.append(f"Over level {MAX_NON_RITUAL} needs a Ritual.")
    design.ritual_required = bool(design.notes)
    if (ritual or design.ritual_required) and level < RITUAL_MINIMUM:
        design.level = RITUAL_MINIMUM
        design.notes.append(f"A Ritual is at least level {RITUAL_MINIMUM}.")
    return design


def extra_magnitudes(
    base: int, range_: str, duration: str, target: str, level: int
) -> int | None:
    """How many magnitudes of size, requisites or troupe ruling a listed
    level carries beyond its base and Range/Duration/Target (None when a
    parameter isn't standard)."""
    design = spell_level(base, range_, duration, target)
    if design is None:
        return None
    count = 0
    probe = design.level
    if level >= probe:
        while probe < level:
            probe = add_magnitudes(probe, 1)
            count += 1
    else:
        while probe > level and probe > 1:
            probe = add_magnitudes(probe, -1)
            count -= 1
    return count


_STANDARD.update(range=RANGE_STEPS, duration=DURATION_STEPS, target=TARGET_STEPS)
