"""Creating the saga's top-level records: a new saga, and a covenant,
character or laboratory added to one. (A Familiar is bound with
familiars.bind_familiar.) Each takes the values a create form collects and
returns the new record; nothing here saves. Covenants, characters and
laboratories start In Creation."""

from __future__ import annotations

import random
from collections.abc import Sequence

from . import seasons, storage
from .arts import ARTS
from .models import (
    Ability,
    ArtScore,
    Character,
    CharacterType,
    Covenant,
    CreationXp,
    KnownSpell,
    LabCharacteristics,
    Laboratory,
    Saga,
    character_age,
)
from .rules import creation_access, creation_covenant, creation_magus


def new_saga(
    name: str, storyguide: str, description: str, year: int, season: str
) -> Saga:
    """A new, empty saga, with an id no saved saga uses."""
    return Saga(
        id=storage.generate_saga_id(name),
        name=name,
        storyguide=storyguide,
        description=description,
        current_year=year,
        current_season=season,
    )


def add_covenant(saga: Saga, name: str, notes: str = "") -> Covenant:
    covenant = Covenant(
        id=storage.generate_unique_id(name, [c.id for c in saga.covenants]),
        saga_id=saga.id,
        name=name,
        notes=notes,
        in_creation=True,
    )
    saga.covenants.append(covenant)
    return covenant


def add_character(
    saga: Saga, name: str, character_type: CharacterType, covenant_id: str | None
) -> Character:
    character = Character(
        id=storage.generate_unique_id(name, [c.id for c in saga.characters]),
        name=name,
        type=character_type,
        covenant_id=covenant_id,
        in_creation=True,
    )
    saga.characters.append(character)
    return character


def add_laboratory(
    saga: Saga,
    name: str,
    size: int,
    covenant_id: str | None,
    *,
    starting: bool = False,
) -> Laboratory:
    """`starting`: one of the covenant's starting laboratories, paid for
    from its Build Points."""
    laboratory = Laboratory(
        id=storage.generate_unique_id(name, [lab.id for lab in saga.laboratories]),
        covenant_id=covenant_id,
        name=name,
        characteristics=LabCharacteristics(size=size),
        in_creation=True,
        starting=starting,
    )
    saga.laboratories.append(laboratory)
    return laboratory


# -- Creation xp --


def _add_xp(character: Character, target: str, xp: int) -> None:
    """Add `xp` (negative: take it off) to the Art or Ability `target`,
    creating the Ability if needed; an Ability left with no xp and no
    specialty is dropped."""
    if target in ARTS:
        key = target.lower()
        score = character.arts.setdefault(key, ArtScore())
        score.xp = max(0, score.xp + xp)
        return
    ability = next((a for a in character.abilities if a.name == target), None)
    if ability is None:
        if xp <= 0:
            return
        ability = Ability(target, creation_access.ability_category(target))
        character.abilities.append(ability)
    ability.xp = max(0, ability.xp + xp)
    if ability.xp == 0 and not ability.specialty:
        character.abilities.remove(ability)


def _applied(entry: CreationXp) -> int:
    return entry.xp if entry.applied is None else entry.applied


def spend_creation_xp(character: Character, entry: CreationXp) -> None:
    """Record `entry` on the worksheet and add its xp to the character (half
    again with an Affinity)."""
    entry.applied = creation_access.effective_xp(character, entry.target, entry.xp)
    character.creation_xp.append(entry)
    _add_xp(character, entry.target, entry.applied)


def change_creation_xp(
    character: Character, entry: CreationXp, target: str, xp: int
) -> None:
    """Move `entry` to `target` / `xp`, taking its old xp back first."""
    _add_xp(character, entry.target, -_applied(entry))
    entry.target, entry.xp = target, xp
    entry.applied = creation_access.effective_xp(character, target, xp)
    _add_xp(character, target, entry.applied)


def refund_creation_xp(character: Character, entry: CreationXp) -> None:
    """Drop `entry` from the worksheet and take its xp back."""
    character.creation_xp.remove(entry)
    _add_xp(character, entry.target, -_applied(entry))


def target_xp(character: Character, target: str) -> int:
    """The total xp the Art or Ability `target` has on the sheet (0: none)."""
    if target in ARTS:
        score = character.arts.get(target.lower())
        return score.xp if score is not None else 0
    ability = next((a for a in character.abilities if a.name == target), None)
    return ability.xp if ability is not None else 0


def gained_xp(entry: CreationXp) -> int:
    """The xp `entry` added to its Art or Ability (half again with an
    Affinity)."""
    return _applied(entry)


def spend_preview(
    character: Character, target: str, xp: int, replacing: CreationXp | None = None
) -> tuple[int, int]:
    """What spending `xp` on `target` would do: the xp it adds (half again
    with an Affinity, rounded up on the whole spend) and the target's total
    xp afterwards. `replacing`: the entry being changed, whose xp comes off
    first."""
    gained = creation_access.effective_xp(character, target, max(xp, 0))
    total = target_xp(character, target)
    if replacing is not None and replacing.target == target:
        total -= _applied(replacing)
    return gained, max(total, 0) + gained


def worksheet_xp(character: Character, target: str) -> tuple[int, int]:
    """While `character` is In Creation, the pool xp its Creation Worksheet
    spent on the Art or Ability `target` and the xp that gained (0, 0: none,
    or In Play)."""
    if not character.in_creation:
        return 0, 0
    found = [x for x in character.creation_xp if x.target == target]
    return sum(x.xp for x in found), sum(_applied(x) for x in found)


def worksheet_note(character: Character, targets: Sequence[str]) -> str:
    """For a sheet dialog that edits total xp: how much of each of
    `targets` came from the Creation Worksheet, and where to take it back
    ("" when none did)."""
    parts = []
    for target in targets:
        spent, gained = worksheet_xp(character, target)
        if gained:
            how = f"{spent} spent x1.5" if gained != spent else f"{spent} spent"
            parts.append(f"{target} {gained} xp ({how})")
    if not parts:
        return ""
    return (
        "From the Creation Worksheet: "
        + ", ".join(parts)
        + ". Take worksheet xp back on the worksheet, not here."
    )


def set_specialty(character: Character, ability_name: str, specialty: str) -> None:
    """Give the Ability `ability_name` its specialty (if it has none or a
    new one is given; an Art has none)."""
    ability = next((a for a in character.abilities if a.name == ability_name), None)
    if ability is not None and specialty:
        ability.specialty = specialty


def learn_creation_spell(
    character: Character, step: str, spell_id: str, level: int
) -> None:
    """A spell learned at a creation step: onto Known Spells, and recorded
    against the step's spell levels."""
    if not any(k.spell_id == spell_id for k in character.spells_known):
        character.spells_known.append(KnownSpell(spell_id=spell_id))
    character.creation_xp.append(CreationXp(step, spell_id, level))


def forget_creation_spell(character: Character, entry: CreationXp) -> None:
    """Undo learn_creation_spell: the record, and the known spell unless
    another step learned it too."""
    character.creation_xp.remove(entry)
    if not any(x.target == entry.target for x in character.creation_xp):
        character.spells_known = [
            k for k in character.spells_known if k.spell_id != entry.target
        ]


def pre_play_aging(saga: Saga, character: Character, rng: random.Random) -> list[str]:
    """Roll the aging a character older than 35 makes before play: one roll
    for each year from 35 (or from where it stopped) up to its age, each
    written in its Diary. A magus uses the years-past-Gauntlet Living
    Conditions; anyone else, their covenant's. Returns each
    roll's summary."""
    years = character_age(character.background.year_born, saga.current_year)
    conditions = character.creation_conditions
    if years is None:
        return []
    start = (
        creation_magus.AGING_AGE
        if conditions.aged_to is None
        else conditions.aged_to + 1
    )
    born = character.background.year_born or saga.current_year - years
    living = conditions.living_conditions if character.type == "magus" else None
    summaries = []
    for age in range(start, years):
        line = seasons.age_character(
            saga,
            character,
            age,
            rng,
            living=living,
            when=("Winter", born + age),
            label=f"Pre-play aging at {age}",
        )
        summaries.append(f"{age}: {line.result}")
        conditions.aged_to = age
    return summaries


def set_in_creation(
    saga: Saga, record: Character | Covenant | Laboratory, in_creation: bool
) -> None:
    """Move `record` to In Creation or In Play. A covenant moving to In Play
    keeps what its Build Points were spent on (the Build tab's Initial
    column); moving back to In Creation lets it change again."""
    record.in_creation = in_creation
    if isinstance(record, Covenant):
        if in_creation:
            record.initial_build_points = None
        else:
            creation_covenant.record_initial(saga, record)
