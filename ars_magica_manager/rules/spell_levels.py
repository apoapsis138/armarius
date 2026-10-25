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

The Mysteries' parameters (EXTRA_PARAMETERS), with their pages:

- Faerie Magic (DE pp. 236-238): Range Road (as Voice); Durations Bargain
  (the triggered effect's own Duration + 3 magnitudes, at most a Year; the
  Penetration Total doubled), Fire (as Moon, on a fire, so Ignem or
  Imaginem), Until (Condition) and Year + 1 (as Year, Ritual); Target
  Bloodline (as Structure). Only a magus with Faerie Magic may learn
  them.
- Spell Timing (DE pp. 239-240): Held and While (Condition) (as
  Concentration), Midday/Midnight and Not (Condition) (as Sun), Season (as
  Moon, Ritual), and If (Condition): the triggered effect's own Duration
  + 4 magnitudes, Ritual. A recurring spell (Ritual) adds +1 (a decade)
  to +5 (a minute) magnitudes by how often it recurs, rounded up to the
  next more frequent row (RECURRING).
- Sensory Magic (Houses of Hermes: Mystery Cults p. 28): Targets Flavor,
  Texture, Scent, Sound and Spectacle, as Individual, Part, Group,
  Structure and Boundary. Spectacle isn't said to need a Ritual, and only
  Boundary itself does (DE p. 311), so it doesn't here.
- Road Magic (The Mysteries Revised Edition p. 116): Range and Target Road
  and Road Network. Mercurian Magic doesn't grant them by itself: such a
  magus learns Road Magic in a season (or has it from a Mercurian parens).
"""

from __future__ import annotations

from dataclasses import dataclass, field

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 9: Spells, Changing Ranges, "
    "Durations, and Targets, pp. 303, 311"
)
#: Targets that contain things: never with Personal Range (DE p. 303).
CONTAINER_TARGETS = ("Circle", "Room", "Structure", "Boundary")

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
    #: Whether only a magus with one of `granted_by` may learn a spell
    #: with it (a Mystery's: Faerie Magic, Spell Timing, Sensory Magic).
    exclusive: bool = False

    @property
    def label(self) -> str:
        """Its name and what it costs, as a select lists it."""
        more = f" +{self.plus}" if self.plus else ""
        return f"{self.name} (as {self.costs_as}{more})"


#: The Durations a triggered effect may have once it takes effect (Event,
#: Bargain, If (Condition)), with the short name its parameter carries.
TRIGGERED: tuple[tuple[str, str], ...] = (
    ("Mom", "Momentary"),
    ("Diam", "Diameter"),
    ("Sun", "Sun"),
    ("Moon", "Moon"),
    ("Year", "Year"),
)
FAERIE_MAGIC = "vf_faerie_magic"
SPELL_TIMING = "vf_spell_timing"
SENSORY_MAGIC = "vf_sensory_magic"
ROAD_MAGIC = "vf_road_magic"
MERCURIAN_MAGIC = "vf_mercurian_magic"


def opening_ids(vf_ids: set[str], *, learned_road: bool) -> set[str]:
    """The Virtues that open parameters for a magus: his own, and Road Magic
    for a Mercurian magus who has learned it, which takes a season's
    teaching and no further Virtue (TMRE p. 116)."""
    if learned_road and MERCURIAN_MAGIC in vf_ids:
        return vf_ids | {ROAD_MAGIC}
    return vf_ids


#: The Mysteries whose parameters only their initiates may learn.
MYSTERY_NAMES: dict[str, str] = {
    FAERIE_MAGIC: "Faerie Magic",
    SPELL_TIMING: "Spell Timing",
    SENSORY_MAGIC: "Sensory Magic",
}
#: Fire Duration is cast on a fire, so the spell is Ignem or Imaginem
#: (DE p. 237).
FIRE_FORMS = ("Ignem", "Imaginem")

EXTRA_PARAMETERS: tuple[ExtraParameter, ...] = (
    ExtraParameter(
        "duration", "Performance", "Concentration", ("vf_performance_magic",)
    ),
    ExtraParameter("range", "Adelphixis", "Arcane Connection", ("vf_orphic_magic",)),
    # Spell Timing (DE pp. 239-240).
    ExtraParameter(
        "duration", "Held", "Concentration", (SPELL_TIMING,), exclusive=True
    ),
    ExtraParameter(
        "duration", "Midday/Midnight", "Sun", (SPELL_TIMING,), exclusive=True
    ),
    ExtraParameter(
        "duration", "Season", "Moon", (SPELL_TIMING,), ritual=True, exclusive=True
    ),
    ExtraParameter(
        "duration",
        "While (Condition)",
        "Concentration",
        (SPELL_TIMING,),
        exclusive=True,
    ),
    ExtraParameter(
        "duration", "Not (Condition)", "Sun", (SPELL_TIMING,), exclusive=True
    ),
    *(
        ExtraParameter(
            "duration",
            f"If ({short})",
            then,
            (SPELL_TIMING,),
            ritual=True,
            plus=4,
            family="If (Condition)",
            exclusive=True,
        )
        for short, then in TRIGGERED
    ),
    # Faerie Magic (DE pp. 237-238); Road is Road Magic's too.
    *(
        ExtraParameter(
            "duration",
            f"Bargain ({short})",
            then,
            (FAERIE_MAGIC,),
            ritual=then == "Year",
            plus=3,
            family="Bargain",
            exclusive=True,
        )
        for short, then in TRIGGERED
    ),
    ExtraParameter("duration", "Fire", "Moon", (FAERIE_MAGIC,), exclusive=True),
    ExtraParameter(
        "duration",
        "Until (Condition)",
        "Year",
        (FAERIE_MAGIC,),
        ritual=True,
        exclusive=True,
    ),
    ExtraParameter(
        "duration", "Year + 1", "Year", (FAERIE_MAGIC,), ritual=True, exclusive=True
    ),
    ExtraParameter("target", "Bloodline", "Structure", (FAERIE_MAGIC,), exclusive=True),
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
    ExtraParameter("range", "Road", "Voice", (ROAD_MAGIC, FAERIE_MAGIC)),
    ExtraParameter(
        "range", "Road Network", "Arcane Connection", (ROAD_MAGIC,), ritual=True
    ),
    ExtraParameter("target", "Road", "Room", (ROAD_MAGIC,)),
    ExtraParameter("target", "Road Network", "Boundary", (ROAD_MAGIC,), ritual=True),
    # Sensory Magic (Houses of Hermes: Mystery Cults p. 28).
    *(
        ExtraParameter("target", name, costs_as, (SENSORY_MAGIC,), exclusive=True)
        for name, costs_as in (
            ("Flavor", "Individual"),
            ("Texture", "Part"),
            ("Scent", "Group"),
            ("Sound", "Structure"),
            ("Spectacle", "Boundary"),
        )
    ),
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
        for short, then in TRIGGERED
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


def parameters_of(range_: str, duration: str, target: str) -> list[ExtraParameter]:
    """The extra parameters among a spell's Range, Duration and Target."""
    found = (
        extra("range", range_),
        extra("duration", duration),
        extra("target", target),
    )
    return [e for e in found if e is not None]


def virtue_needed(
    vf_ids: set[str], range_: str, duration: str, target: str
) -> list[str]:
    """Why a magus with these Virtue/Flaw ids may not learn or invent a
    spell with these parameters: a Mystery's own (Faerie Magic, Spell
    Timing, Sensory Magic) needs that Mystery (DE pp. 236, 239; HoH:MC p.
    28). Empty when nothing stops him."""
    found: list[str] = []
    for kind, name in (("range", range_), ("duration", duration), ("target", target)):
        e = extra(kind, name)
        if e is None or not e.exclusive or any(v in vf_ids for v in e.granted_by):
            continue
        needs = " or ".join(MYSTERY_NAMES.get(v, v) for v in e.granted_by)
        found.append(f"{name} {kind.title()} needs {needs}.")
    return found


#: Recurring spells (Spell Timing, DE p. 240): how often it may recur ->
#: the magnitudes it adds. A frequency between rows takes the more
#: frequent row's (every ten minutes is +5); never more than once a minute.
RECURRING: dict[str, int] = {
    "minute": 5,
    "day": 4,
    "month": 3,
    "year": 2,
    "decade": 1,
}
RECURRING_SOURCE = (
    "Ars Magica Definitive Edition, Spell Timing, Recurring Spells, p. 240"
)


def recurring_magnitudes(frequency: str) -> int:
    """The magnitudes recurring once a `frequency` adds (0 for "": it
    doesn't recur). ValueError for a frequency not on the table."""
    if not frequency:
        return 0
    if frequency not in RECURRING:
        raise ValueError(f"A spell can't recur each {frequency!r}.")
    return RECURRING[frequency]


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


#: A lasting thing made by Creo needs the power of a Ritual.
MOMENTARY_CREO = (
    "A Momentary Creo spell that creates a lasting thing must be a Ritual (DE p. 311)."
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
    technique: str = "",
    form: str = "",
    recurring: str = "",
) -> Design | None:
    """The level of a spell with this base and Range/Duration/Target, plus
    `extra_magnitudes` of size and requisites. A parameter a Virtue or
    Mystery grants costs as its standard counterpart; `custom_steps` gives
    the magnitudes of any other ("range"/"duration"/"target" -> n: a
    breakthrough or a troupe ruling). Given the `technique`, a Momentary
    Creo spell that isn't a Ritual gets a note: what it creates vanishes
    unless the spell is a Ritual (DE p. 311). A spell recurring each
    `recurring` (a RECURRING key) adds its magnitudes and must be a Ritual;
    given the `form`, a Fire Duration spell not of Ignem or Imaginem gets a
    note. None when a parameter is unknown."""
    custom = custom_steps or {}
    steps = []
    for kind, name in (("range", range_), ("duration", duration), ("target", target)):
        count = custom.get(kind, steps_of(kind, name))
        if count is None:
            return None
        steps.append((name, count))
    if extra_magnitudes:
        steps.append(("size/requisites", extra_magnitudes))
    if recurring:
        steps.append((f"recurs each {recurring}", recurring_magnitudes(recurring)))
    level = add_magnitudes(base, sum(n for _, n in steps))
    design = Design(level=level, steps=steps)
    for kind, name in (("range", range_), ("duration", duration), ("target", target)):
        if needs_ritual(kind, name):
            design.notes.append(f"{name} {kind.title()} needs a Ritual.")
    if recurring:
        design.notes.append("A recurring spell needs a Ritual (DE p. 240).")
    if level > MAX_NON_RITUAL:
        design.notes.append(f"Over level {MAX_NON_RITUAL} needs a Ritual.")
    design.ritual_required = bool(design.notes)
    if (ritual or design.ritual_required) and level < RITUAL_MINIMUM:
        design.level = RITUAL_MINIMUM
        design.notes.append(f"A Ritual is at least level {RITUAL_MINIMUM}.")
    if technique == "Creo" and duration == "Momentary" and not ritual:
        design.notes.append(MOMENTARY_CREO)
    if duration == "Fire" and form and form not in FIRE_FORMS:
        design.notes.append(
            "Fire Duration is cast on a fire: the spell must be Ignem or "
            "Imaginem (DE p. 237)."
        )
    if range_ == "Personal" and target in CONTAINER_TARGETS:
        design.notes.append(
            f"A Personal Range spell can't have a {target} Target (DE p. 303)."
        )
    return design


def extra_magnitudes(
    base: int,
    range_: str,
    duration: str,
    target: str,
    level: int,
    *,
    ritual: bool = False,
) -> int | None:
    """How many magnitudes of size, requisites or troupe ruling a listed
    level carries beyond its base and Range/Duration/Target (None when a
    parameter isn't standard). A Ritual listed at its level-20 floor
    carries none (DE p. 311)."""
    design = spell_level(base, range_, duration, target)
    if design is None:
        return None
    if ritual and design.level < RITUAL_MINIMUM and level <= RITUAL_MINIMUM:
        return 0
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
