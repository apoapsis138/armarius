"""Ancient Magic's lost magics as the app reads them: the chapters'
integration data (ancient_magic_catalog.json) and the small rules that
use it.

- Integration (DE pp. 279-281, Ancient Magic pp. 7-9): Insight from a
  text, relic or teacher, an effect invented from it for its magnitude in
  breakthrough points. The catalog names each chapter's sources, the Arts
  of the effects, and the Breakthroughs rules.integrations lacks.
- Grigori Magic (pp. 65-74): a Secret makes vis of its Technique and two
  Forms interchangeable and drops requisites among them; tainted, it
  doubles the botch dice in a Divine or Infernal aura (a Legacy doesn't).
  A holder of a Secret (or, for the Limit of Vis, a Legacy) gains a
  breakthrough point a season researching its integration (p. 67).
- Heron's mechanica (pp. 76-80, Errata p. 58): the Creation Level, the
  anima's Might and Awaken level, the one-time bonus for copying a
  mechanica Hermetically, Mutable and Awakened Devices.
- The Language of Adam (pp. 10-11): +1 to the Penetration multiplier for
  a target named in Adamic, and fluency's lasting Arcane Connections.
- The Hesperides (pp. 89-92, Errata p. 58): the stellar observation that
  gives Ptolemaic coordinates, which never fade.

Pattern: the chapters are catalog data (Type Object records) read by
plain functions; the one season it adds goes through the season
registry (season_work/ancient.py).
"""

from __future__ import annotations

from collections.abc import Sequence

from .. import catalog
from ..models import Breakthrough, Character
from ..models.ancient_magic import AncientChapter, GrigoriSecret, IntegrationNote
from .lab import ability_score
from .penetration import ARCANE_CONNECTIONS, Sympathy
from .powers import magnitude
from .rounding import round_down

SOURCE = (
    "Ancient Magic, Introduction pp. 7-9, The Language of Adam pp. 10-11, "
    "Grigori Magic pp. 65-74, Heron of Alexandria's Legacy pp. 75-80, The "
    "Hesperides pp. 89-92; Errata p. 58; Ars Magica Definitive Edition, "
    "Arcane Discovery, pp. 277-281"
)

ADAMIC_ID = "am_adamic"
GRIGORI_ID = "am_grigori"
HERON_ID = "am_heron"
HESPERIDES_ID = "am_hesperides"


def chapters() -> tuple[AncientChapter, ...]:
    return tuple(catalog.load_ancient_magic_catalog())


def chapter(chapter_id: str) -> AncientChapter:
    found = next((c for c in chapters() if c.id == chapter_id), None)
    if found is None:
        raise LookupError(f"No Ancient Magic chapter {chapter_id!r}")
    return found


def _value(chapter_id: str, key: str) -> int:
    values = chapter(chapter_id).values
    if key not in values:
        raise LookupError(f"Ancient Magic chapter {chapter_id!r} has no {key!r}")
    return values[key]


def _holds(character: Character, vf_id: str) -> bool:
    return any(vf.vf_id == vf_id for vf in character.virtues_flaws)


# -- integrations ---------------------------------------------------------


def note_for(name: str) -> IntegrationNote | None:
    """What a chapter says of the integration called `name`."""
    key = name.strip().lower()
    return next(
        (n for c in chapters() for n in c.integrations if n.name.lower() == key),
        None,
    )


def chapter_of(name: str) -> AncientChapter | None:
    """The chapter an integration belongs to."""
    key = name.strip().lower()
    return next(
        (c for c in chapters() if any(n.name.lower() == key for n in c.integrations)),
        None,
    )


def season_bonus(character: Character, goal: Breakthrough) -> int:
    """The extra breakthrough points a season of research toward `goal`
    gives this magus: a Grigori Secret held while integrating its Legacy,
    a Secret or Legacy for the Limit of Vis (p. 67)."""
    note = note_for(goal.name)
    if note is None or not note.bonus_points or goal.reached:
        return 0
    if any(_holds(character, vf_id) for vf_id in note.bonus_virtues):
        return note.bonus_points
    return 0


def apply_season_bonus(character: Character, goal: Breakthrough) -> list[str]:
    """The season's extra points added to the goal; its Diary line."""
    bonus = season_bonus(character, goal)
    if not bonus:
        return []
    goal.points += bonus
    return [
        f"A Secret of the Grigori held: +{bonus} breakthrough point toward "
        f"{goal.name} ({goal.points}/{goal.target}; Ancient Magic p. 67)."
    ]


def missing_prerequisite(character: Character, name: str) -> str:
    """The integration `name` builds on, when the magus hasn't reached it
    ("" when nothing is missing)."""
    note = note_for(name)
    if note is None or not note.requires:
        return ""
    want = note.requires.lower()
    if any(b.reached and b.name.lower() == want for b in character.breakthroughs):
        return ""
    return note.requires


def goal_lines(goal: Breakthrough) -> list[str]:
    """Lines (plain text) for a research goal's details: the chapter's
    effects and Insight sources, its season bonus, what it builds on."""
    note = note_for(goal.name)
    found = chapter_of(goal.name)
    if note is None or found is None:
        return []
    pages = note.pages or found.pages
    lines: list[str] = []
    if note.effect:
        arts = f" ({note.arts})" if note.arts else ""
        lines.append(
            f"Insights give{arts}: {note.effect} (Ancient Magic, {found.name}, "
            f"p. {pages})"
        )
    sources = [s for s in found.insight_sources if s.insight]
    if sources:
        lines.append(
            "Sources of Insight: "
            + "; ".join(f"{s.name} ({s.kind}, p. {s.pages})" for s in sources)
            + "."
        )
    if note.bonus_points:
        names = _vf_names(note.bonus_virtues)
        lines.append(
            f"+{note.bonus_points} breakthrough point a season of its research "
            f"for a holder of {names}."
        )
    if note.requires:
        lines.append(f"Builds on {note.requires}, which must be reached first.")
    return lines


def _vf_names(vf_ids: Sequence[str]) -> str:
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    named = [by_id[v].name if v in by_id else v for v in vf_ids]
    if len(named) > 3:
        return "a Secret of the Grigori" + (
            " or a Grigori Legacy" if "vf_grigori_legacy" in vf_ids else ""
        )
    return " or ".join(named)


# -- Grigori Magic --------------------------------------------------------

GRIGORI_LEGACY = "vf_grigori_legacy"
TAINTED_REALMS = ("Divine", "Infernal")


def secrets() -> tuple[GrigoriSecret, ...]:
    return chapter(GRIGORI_ID).secrets


def _legacy_secret(param: str) -> GrigoriSecret | None:
    """The Secret a Grigori Legacy's parameter names (the chief's name, or
    the Secret's)."""
    # The book spells the first chief both Araqiel and Araquiel.
    key = param.strip().lower().replace("araquiel", "araqiel")
    if not key:
        return None
    for secret in secrets():
        chief = secret.name.split()[0].lower()
        chief = chief.removesuffix("'s")
        if key in secret.name.lower() or chief in key:
            return secret
    return None


def held_secrets(character: Character) -> list[tuple[GrigoriSecret, bool]]:
    """Each Secret the character can use, and whether it is tainted (held
    as the Supernatural Virtue and not also as a Legacy)."""
    legacies = {
        found.vf_id
        for vf in character.virtues_flaws
        if vf.vf_id == GRIGORI_LEGACY
        and (found := _legacy_secret(vf.params.get("secret", ""))) is not None
    }
    held: list[tuple[GrigoriSecret, bool]] = []
    for secret in secrets():
        if secret.vf_id in legacies:
            held.append((secret, False))
        elif _holds(character, secret.vf_id):
            held.append((secret, True))
    return held


def interchangeable_vis(character: Character, art: str) -> list[str]:
    """The Arts whose vis this character may use as `art`'s vis."""
    found: set[str] = set()
    for secret, _ in held_secrets(character):
        if art in secret.arts:
            found.update(a for a in secret.arts if a != art)
    return sorted(found)


def ignored_requisites(
    character: Character, technique: str, form: str, requisites: Sequence[str]
) -> list[str]:
    """The requisites a spell of `technique` and `form` may ignore: those
    among a held Secret's Arts, when the spell uses another of them."""
    ignored: list[str] = []
    for secret, _ in held_secrets(character):
        if technique not in secret.arts and form not in secret.arts:
            continue
        ignored += [r for r in requisites if r in secret.arts and r not in ignored]
    return ignored


def vis_botch_dice(
    character: Character, dice: int, vis_art: str, used_for: str, aura_realm: str
) -> int:
    """Botch dice for vis of `vis_art` used as `used_for`'s: doubled in a
    Divine or Infernal aura when only a tainted Secret allows it."""
    if vis_art == used_for or aura_realm not in TAINTED_REALMS:
        return dice
    ways = [
        tainted
        for secret, tainted in held_secrets(character)
        if vis_art in secret.arts and used_for in secret.arts
    ]
    if ways and all(ways):
        return dice * _value(GRIGORI_ID, "tainted_botch_multiplier")
    return dice


# -- Heron's mechanica ----------------------------------------------------

#: The Mechanica Creation Level's size modifiers (p. 77).
MECHANICA_SIZES: dict[str, int] = {
    "Human-sized or larger": 0,
    "Wagon- or boat-sized": -3,
    "Easily carried": 3,
    "Hand-sized": 6,
}
#: An effect taking 15 minutes a magnitude to employ (p. 77).
EXTRA_TIME = -3


def mechanica_creation_level(
    effect_magnitude: int, size: str = "Human-sized or larger", extra_time: bool = False
) -> int:
    """3 x the imbued effect's magnitude + its modifiers (Errata p. 58),
    reductions never taking it below 3 (p. 77). Altering one sets the
    same level for the new effect as its Ease Factor."""
    if size not in MECHANICA_SIZES:
        raise ValueError(f"Unknown mechanica size {size!r}")
    level = 3 * effect_magnitude + MECHANICA_SIZES[size]
    if extra_time:
        level += EXTRA_TIME
    return max(_value(HERON_ID, "minimum_creation_level"), level)


def mechanica_cost(creation_level: int) -> int:
    """Mythic Pounds: one per 3 Creation Levels (p. 77)."""
    return round_down(creation_level / _value(HERON_ID, "creation_levels_per_pound"))


def mechanica_total(character: Character, aura: int = 0) -> int:
    """Construct (and Awaken) Total: Intelligence + Mechanica of Heron +
    the lower of Philosophiae and Artes Liberales + aura (pp. 77-78)."""
    return (
        character.characteristics.intelligence
        + sum(ability_score(character, "Mechanica of Heron"))
        + _lower_learning(character)
        + aura
    )


def _lower_learning(character: Character) -> int:
    return min(
        sum(ability_score(character, "Philosophiae")),
        sum(ability_score(character, "Artes Liberales")),
    )


def anima_might(character: Character, size: int, material_points: int) -> int:
    """An anima's Magic Might: its Size + its material's base points + the
    lower of Philosophiae and Artes Liberales (p. 78). It costs a Mythic
    Pound a point."""
    return size + material_points + _lower_learning(character)


def anima_points_a_season(character: Character) -> int:
    """Might points built into a simulacrum a season: Mechanica of Heron +
    Intelligence (p. 78)."""
    return sum(ability_score(character, "Mechanica of Heron")) + (
        character.characteristics.intelligence
    )


def awaken_anima_level(might: int) -> int:
    """9 + the magnitude of the anima's Magic Might (p. 78)."""
    return _value(HERON_ID, "awaken_anima_base") + magnitude(might)


def awaken_anima_total(character: Character, aura: int = 0, season: int = 1) -> int:
    """The Awaken Total, +1 for each season after the first (p. 78)."""
    return mechanica_total(character, aura) + max(0, season - 1)


def copy_bonus(
    *, effect_magnitude: int = 0, text_level: int = 0, text_quality: int = 0
) -> int:
    """The one-time Lab Total bonus for a Hermetic device copying a
    mechanica: its effect's magnitude, or a text's Level or Quality,
    whichever is lower (p. 76)."""
    if effect_magnitude:
        return effect_magnitude
    return min(text_level, text_quality)


def mutable_device_level(effect_level: int) -> int:
    """A Mutable Device's level: its effect's + 10 (p. 79)."""
    return effect_level + _value(HERON_ID, "mutable_device_levels")


def mutable_change_allowed(device_level: int, new_effect_level: int) -> bool:
    """A Mutable Device's new effect, with the property's +10, must be no
    higher than the level it has (p. 79)."""
    return mutable_device_level(new_effect_level) <= device_level


def awakened_device_might(material_points: int, magic_theory: int) -> int:
    """Awaken Device: Might = material base points + Magic Theory (p. 80)."""
    return material_points + magic_theory


def awakened_device_level(might: int, size: int) -> int:
    """Awakened Device Level: its Might + Size x 5 (p. 80)."""
    return might + size * 5


def awakened_device_vis(opening_pawns: int, might: int) -> int:
    """Vim vis to open it as an enchanted device, + a pawn of Creo or the
    Form a point of Might (p. 80)."""
    return opening_pawns + might


# -- The Language of Adam -------------------------------------------------

ADAMIC = "Dead Language: Adamic"
NAMED_IN_ADAMIC = "Named in Adamic"
#: How a fluent speaker's connection to a mundane thing he knows the name
#: of counts for Penetration (p. 10).
MUNDANE_NAME_CONNECTION = "Hours or days"
#: A connection that never fades (a fluent speaker's naming; a Ptolemaic
#: coordinate).
LASTING_CONNECTION = "Indefinitely"


def adamic_score(character: Character) -> int:
    return sum(ability_score(character, ADAMIC))


def adamic_fluent(character: Character) -> bool:
    return adamic_score(character) >= _value(ADAMIC_ID, "fluent_score")


def adamic_penetration(
    character: Character, arcane_connection: str | None = None
) -> tuple[str | None, list[Sympathy]]:
    """The Arcane Connection and sympathies for a target named in Adamic
    within Voice range: any Adamic adds +1 to the multiplier, with an
    Arcane Connection until the speaker is fluent; fluent, his naming is a
    lasting connection (p. 10). Pass them to penetration.penetration_bonus."""
    if not adamic_score(character):
        return arcane_connection, []
    bonus = Sympathy(NAMED_IN_ADAMIC, _value(ADAMIC_ID, "penetration_multiplier"))
    if adamic_fluent(character):
        best = arcane_connection
        if best is None or (
            ARCANE_CONNECTIONS[best] < ARCANE_CONNECTIONS[LASTING_CONNECTION]
        ):
            best = LASTING_CONNECTION
        return best, [bonus]
    if arcane_connection is None:
        return None, []
    return arcane_connection, [bonus]


def adamic_untaught_cap() -> int:
    """The most a Gifted child raised apart from language reaches in
    Adamic without instruction (p. 11)."""
    return _value(ADAMIC_ID, "wild_child_score")


# -- The Hesperides: Ptolemaic coordinates --------------------------------

MEASURING = "Measuring the fixed stars"
MEASURING_KIND = "ptolemy"
OBSERVATION_ABILITY = "Artes Liberales"


def knows_stellar_measurement(character: Character) -> bool:
    """Whether the character has spent the season learning to measure the
    array of fixed stars (p. 90)."""
    return any(
        p.kind == MEASURING_KIND and p.name == MEASURING and p.done
        for p in character.progress
    )


def observation_ease() -> int:
    return next(
        r.ease
        for r in chapter(HESPERIDES_ID).rolls
        if r.total.endswith(OBSERVATION_ABILITY) and r.ease is not None
    )


def observation_total(character: Character, handy_tables: bool = False) -> int:
    """Intelligence + Artes Liberales, +1 with sound copies of the Handy
    Tables (p. 90), before the die; it must reach the Ease Factor."""
    total = character.characteristics.intelligence + sum(
        ability_score(character, OBSERVATION_ABILITY)
    )
    if handy_tables:
        total += _value(HESPERIDES_ID, "handy_tables_bonus")
    return total


def observation_hours(timepiece: bool = False, tables: str = "") -> int:
    """Hours a stellar observation takes: watching the stars (halved with
    a supernaturally accurate timepiece) and the calculations ("greatest":
    the Greatest Compilation's tables; "handy": the Handy Tables; p. 90)."""
    watching = _value(
        HESPERIDES_ID,
        "observation_hours_timepiece" if timepiece else "observation_hours",
    )
    key = {
        "": "calculation_hours",
        "greatest": "calculation_hours_greatest_compilation",
        "handy": "calculation_hours_handy_tables",
    }.get(tables)
    if key is None:
        raise ValueError(f"Unknown tables {tables!r}")
    return watching + _value(HESPERIDES_ID, key)


def coordinates_problems(character: Character, calibrated: bool) -> list[str]:
    """What stops the character deriving new coordinates: the measuring
    not learned, the system not calibrated at the origin (pp. 90-91)."""
    problems: list[str] = []
    if not knows_stellar_measurement(character):
        problems.append("Learn to measure the fixed stars (a season).")
    if not calibrated:
        problems.append("Calibrate the system at the origin (the Purple Islands).")
    return problems


# -- the casting panel's reminders ----------------------------------------


def casting_lines(character: Character) -> list[str]:
    """Plain-text reminders for the casting panel: Adamic's Penetration,
    the Grigori Secrets' vis and requisites."""
    lines: list[str] = []
    score = adamic_score(character)
    if score:
        if adamic_fluent(character):
            lines.append(
                f"Adamic {score} (fluent): a target named within Voice range is a "
                "lasting Arcane Connection (+4) and +1 more to the Penetration "
                "multiplier; a mundane thing whose name is known counts as Hours "
                "(Ancient Magic p. 10)."
            )
        else:
            lines.append(
                f"Adamic {score}: +1 to the Penetration multiplier naming a target "
                "within Voice range, with an Arcane Connection to it (Ancient "
                "Magic p. 10)."
            )
    for secret, tainted in held_secrets(character):
        arts = ", ".join(secret.arts)
        line = (
            f"{secret.name}: vis of {arts} may stand for one another, and their "
            "requisites among them are ignored"
        )
        if tainted:
            line += (
                "; in a Divine or Infernal aura such vis, or a botch of a spell "
                "that ignored a requisite so, rolls double the botch dice"
            )
        lines.append(line + " (Ancient Magic p. 67).")
    return lines
