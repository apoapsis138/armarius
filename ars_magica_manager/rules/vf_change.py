"""Gaining and losing Virtues and Flaws during the saga (Grogs pp. 61-64,
with the Definitive Edition's limits, DE p. 63, and Warping, DE p. 391).

- A Flaw comes by mishap (an injury, an amputation, a disease), by the
  character's own actions (a feud, a debt, a changed social status,
  offending a faerie) or by magic (a curse, a creature's Might spent,
  Warping). It is a Flaw only if it affects the game, seeds stories or
  changes how the character is played (Grogs p. 62).
- A Virtue comes by magic (most such grants are temporary; a permanent
  one from a supernatural being, the Goetic Arts or severe Warping), by
  Initiation (which needs a score in the cult's or tradition's
  Organization Lore first) or by actions (an agent recruited, a powerful
  friend made). A Virtue that changes how experience is gained doesn't
  recalculate experience already gained (Grogs pp. 62-63).
- A Virtue or Flaw gained by magic is usually for a while: most magical
  grants of a Virtue are temporary (a gruagach's spells, an Object of
  Virtue, faerie wizardry), and hedge curses that lay a Flaw are usually
  limited in duration (Grogs pp. 62-63). Such a one is marked temporary,
  with the season it ends if that is known, and lapses in play.
- A grog should not gain a Story Flaw unless it is temporary or he is
  becoming a companion, and the troupe should be cautious about his
  gaining a Major Virtue for the same reason (Grogs pp. 62-63).
- A Flaw is lost by most of the ways a Virtue is gained, though not every
  way suits every Flaw: a lost hand isn't restored by Initiation, only by
  supernatural means (Grogs p. 63).
- A change of Social Status replaces the old status with the new one;
  only a status whose description says so is kept beside it (Grogs p. 61).
- With the troupe's approval a Virtue or Flaw chosen wrongly may be
  exchanged: for an established character only Minor for Minor and Major
  for Major on the same side, never one that changes Characteristics or
  Abilities, and never one that has been a major feature of a story; a
  character new to the saga may change more freely (Grogs p. 61).
- The Definitive Edition's guidelines still hold in play: one Story Flaw
  at most (a guideline), never more than one Major Personality Flaw, and
  at most two Personality Flaws (one for a grog) (DE p. 63). Warping gives
  a non-magus Minor Flaws at Scores 1 and 3, a Minor supernatural Virtue
  at 5 and a Major Flaw at 6 and after; a magus's Twilight brings its own
  (DE pp. 229-230, 391).

The Errata (pp. 13, 83) correct nothing on Grogs pp. 61-64.
"""

from __future__ import annotations

from ..models import SEASONS, Character, VirtueFlawDef, VirtueFlawInstance
from ..models.seasons import season_order
from . import warping
from .scores import ability_level

SOURCE = (
    "Grogs, Chapter Five: Creating & Maintaining Grogs, Virtues and Flaws, pp. 61-64"
)
DE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 4: Virtues and Flaws Rules and "
    "Guidelines, p. 63"
)

#: What changes, in the form's order.
GAIN_FLAW, GAIN_VIRTUE, LOSE_FLAW, TEMPORARY_ENDS, SOCIAL_STATUS, EXCHANGE = (
    "gain_flaw",
    "gain_virtue",
    "lose_flaw",
    "temporary_ends",
    "social_status",
    "exchange",
)
CHANGES: dict[str, str] = {
    GAIN_FLAW: "Gain a Flaw",
    GAIN_VIRTUE: "Gain a Virtue",
    LOSE_FLAW: "Lose a Flaw",
    TEMPORARY_ENDS: "A temporary Virtue or Flaw ends",
    SOCIAL_STATUS: "A change of Social Status",
    EXCHANGE: "Exchange one chosen wrongly",
}

#: What the book says of a Virtue or Flaw gained by magic for a while.
TEMPORARY_RULE = (
    "Most Virtues granted by magic are temporary (a gruagach's spells, an "
    "Object of Virtue, faerie wizardry), and hedge curses that lay Flaws are "
    "usually limited in duration (Grogs pp. 62-63)."
)

MISHAP, ACTIONS, MAGIC, WARPING, INITIATION, STORY = (
    "mishap",
    "actions",
    "magic",
    "warping",
    "initiation",
    "story",
)

#: How a Flaw is gained: its label and what the book says of it.
FLAW_CAUSES: dict[str, tuple[str, str]] = {
    MISHAP: (
        "Mishap: injury, amputation, disease",
        "Most often a General Flaw of the body: a lost hand is always the "
        "Missing Hand Flaw (Grogs p. 62).",
    ),
    ACTIONS: (
        "Their own actions",
        "A feud, a debt to the powerful, an animal companion, offending a "
        "faerie (a Malediction or a disfigurement); a Story Flaw needs the "
        "storyguide's approval (Grogs p. 62).",
    ),
    MAGIC: (
        "Magic: a curse",
        "Hedge curses (an infernalist's Malediction, a faerie wizard's "
        "Grant) are usually limited in duration; a creature spending Might "
        "lays a permanent one, which a story may yet undo (Grogs p. 62).",
    ),
    WARPING: (
        "Warping",
        "Warping brings Flaws to anyone not aligned to a realm (Grogs p. 62; "
        "DE p. 391).",
    ),
}

#: How a Virtue is gained.
VIRTUE_CAUSES: dict[str, tuple[str, str]] = {
    MAGIC: (
        "Magic: a supernatural being's gift",
        "Most magical grants are temporary; a permanent one comes from a "
        "supernatural being (spending Might) or the Goetic Arts, and is never "
        "frivolous: the story needs it or seeks it (Grogs p. 63).",
    ),
    INITIATION: (
        "Initiation into a cult or tradition",
        "The Initiation pays for the Virtue in Ordeals, quests, sacrifices "
        "and study (Grogs p. 63; TMRE Chapter 2).",
    ),
    ACTIONS: (
        "Their own actions in a story",
        "Usually from dealings with storyguide characters: Social Contacts "
        "for an agent recruited, Protection for an influential friend, if "
        "more than a passing association (Grogs p. 63).",
    ),
    WARPING: (
        "Warping",
        "Severe Warping may bring a Virtue reflecting the power behind it "
        "(Grogs p. 63; DE p. 391).",
    ),
}

#: How a Flaw is lost.
LOSS_CAUSES: dict[str, tuple[str, str]] = {
    MAGIC: (
        "Supernatural means",
        "Magic can rid a character of a Flaw that no ordinary means will, "
        "such as a lost hand (Grogs p. 63).",
    ),
    INITIATION: (
        "Initiation",
        "Not every Flaw yields to Initiation: a Missing Hand cannot grow back "
        "that way (Grogs p. 63).",
    ),
    STORY: (
        "A story: a curse lifted, a debt paid",
        "A story may rid the character of a curse, a feud or a debt (Grogs p. 63).",
    ),
}

#: The modifier types that change how experience is gained.
XP_MODIFIERS = frozenset(
    {
        "ability_xp_gain",
        "art_xp_gain",
        "study_total",
        "advancement_total",
        "book_quality",
        "teaching_source_quality",
    }
)
#: The modifier types that change an Ability's or Art's score.
ABILITY_MODIFIERS = frozenset(
    {"ability_score_effective", "ability_xp_gain", "art_score_effective", "art_xp_gain"}
)


def in_category(entry: VirtueFlawDef, category: str) -> bool:
    """Whether `entry` is of the type `category` ("Social Status"), as its
    main type or one of its others."""
    return category in (entry.category, *entry.extra_categories)


def is_social_status(entry: VirtueFlawDef) -> bool:
    return in_category(entry, "Social Status")


def _held(character: Character, by_id: dict[str, VirtueFlawDef]) -> list[VirtueFlawDef]:
    return [
        entry
        for vf in character.virtues_flaws
        if (entry := by_id.get(vf.vf_id)) is not None
    ]


def organization_lores(character: Character) -> list[str]:
    """The character's Organization or cult Lores with a score: what
    Initiation asks for first (Grogs p. 63)."""
    return [
        a.name
        for a in character.abilities
        if (
            a.name.startswith(("Organization Lore", "Mystery Cult Lore"))
            or a.name.endswith("Cult Lore")
        )
        and ability_level(character, a.name) > 0
    ]


def gain_refusal(
    character: Character, entry: VirtueFlawDef, by_id: dict[str, VirtueFlawDef]
) -> str:
    """Why `character` can't gain `entry` in play ("" if they can): a second
    Major Personality Flaw (DE p. 63), or a Social Status while they hold
    one, which is a change of status (Grogs p. 61)."""
    held = _held(character, by_id)
    if (
        entry.side == "Flaw"
        and in_category(entry, "Personality")
        and entry.tier == "Major"
        and any(
            h.side == "Flaw" and in_category(h, "Personality") and h.tier == "Major"
            for h in held
        )
    ):
        return (
            "A character may not have more than one Major Personality Flaw (DE p. 63)."
        )
    if is_social_status(entry) and any(is_social_status(h) for h in held):
        return (
            f"{entry.name} is a Social Status: choose A change of Social Status, "
            "which replaces the old one (Grogs p. 61)."
        )
    return ""


def gain_notes(
    character: Character,
    entry: VirtueFlawDef,
    by_id: dict[str, VirtueFlawDef],
) -> list[str]:
    """What the books warn of when `character` gains `entry` in play."""
    held = _held(character, by_id)
    grog = character.type == "grog"
    found: list[str] = []
    if entry.side == "Flaw":
        found.append(
            "A Flaw only if it affects the game, seeds stories or changes how "
            "they are played (Grogs p. 62)."
        )
    if grog and entry.side == "Virtue" and entry.tier == "Major":
        found.append(
            "A grog gaining a Major Virtue: the troupe should be cautious, "
            "unless he is becoming a companion (Grogs p. 63)."
        )
    if in_category(entry, "Story"):
        if grog:
            found.append(
                "A grog shouldn't gain a Story Flaw unless it is temporary or he "
                "is becoming a companion (Grogs p. 62)."
            )
        if any(in_category(h, "Story") for h in held):
            found.append(
                "They have a Story Flaw already: more than one needs the whole "
                "troupe's agreement (DE p. 63)."
            )
    if entry.side == "Flaw" and in_category(entry, "Personality"):
        most = 1 if grog else 2
        count = sum(
            1 for h in held if h.side == "Flaw" and in_category(h, "Personality")
        )
        if count + 1 > most:
            found.append(
                f"That makes {count + 1} Personality Flaws; "
                f"{'a grog' if grog else 'a character'} should have no more than "
                f"{most} (DE p. 63)."
            )
    if entry.side == "Virtue" and any(
        m.applies_to in XP_MODIFIERS for m in entry.modifiers
    ):
        found.append(
            "Experience already gained isn't recalculated for it (Grogs p. 62)."
        )
    return found


def initiation_note(character: Character) -> str:
    """Whether the character has the Lore Initiation needs (Grogs p. 63)."""
    lores = organization_lores(character)
    if lores:
        return f"Initiated through {', '.join(lores)}."
    return (
        "Initiation needs a score in the cult's or tradition's Organization "
        "Lore first, and none is on the sheet (Grogs p. 63)."
    )


def warping_notes(character: Character) -> list[str]:
    """What the character's Warping Score has brought them (DE p. 391), or
    for a magus, where Twilight's Virtues and Flaws come from."""
    if character.type == "magus":
        return [
            "A magus's Warping brings Virtues and Flaws through Wizard's "
            "Twilight (DE pp. 229-230)."
        ]
    if warping.immune(character):
        return ["A Might score makes them part of a realm: Warping doesn't touch them."]
    score = character.aging.warping_score
    if score <= 0:
        return [
            "Warping Score 0: a non-magus gains their first Minor Flaw at "
            "Score 1 (DE p. 391)."
        ]
    return [f"So far: {line}" for line in warping.mundane_effects(0, score)]


def loss_notes(entry: VirtueFlawDef, cause: str) -> list[str]:
    """What the book warns of when `entry` is lost by `cause`."""
    if cause == INITIATION and in_category(entry, "General"):
        return [
            f"{entry.name} is a General Flaw: one of the body (a lost hand) "
            "yields only to supernatural means, not Initiation (Grogs p. 63)."
        ]
    return []


def exchange_refusal(old: VirtueFlawDef, new: VirtueFlawDef, new_to_saga: bool) -> str:
    """Why `old` can't be exchanged for `new` ("" if it can): a Virtue for
    a Virtue and a Flaw for a Flaw, and for an established character a
    Minor for a Minor and a Major for a Major (Grogs p. 61)."""
    if old.side != new.side:
        return f"A {old.side} is exchanged only for another {old.side} (Grogs p. 61)."
    if not new_to_saga and old.tier != new.tier:
        return (
            f"An established character exchanges a {old.tier} {old.side} only for "
            f"another {old.tier} one (Grogs p. 61)."
        )
    if is_social_status(old) or is_social_status(new):
        return (
            "A Social Status is changed with A change of Social Status (Grogs p. 61)."
        )
    return ""


def exchange_notes(old: VirtueFlawDef, new: VirtueFlawDef) -> list[str]:
    """The exchange's cautions: Abilities changed, and a story's feature."""
    found = []
    for entry in (old, new):
        if entry.category == "Supernatural" or any(
            m.applies_to in ABILITY_MODIFIERS for m in entry.modifiers
        ):
            found.append(
                f"{entry.name} touches the character's Abilities: such changes "
                "should not be made (Grogs p. 61)."
            )
    found.append(
        "Never discard one that has been a major feature of a story (Grogs p. 61)."
    )
    return found


def status_refusal(old: VirtueFlawDef, new: VirtueFlawDef) -> str:
    """Why `old` can't become `new` as a change of Social Status."""
    if not is_social_status(old):
        return f"{old.name} is not a Social Status."
    if not is_social_status(new):
        return f"{new.name} is not a Social Status."
    if old.id == new.id:
        return f"They are {old.name} already."
    return ""


# -- a Virtue or Flaw gained for a while --


def ends_text(instance: VirtueFlawInstance) -> str:
    """When a temporary Virtue or Flaw ends: "Winter 1225", "the end of
    1225" (a year alone), or "" when no end is set."""
    if instance.ends_year is None:
        return ""
    if instance.ends_season in SEASONS:
        return f"{instance.ends_season} {instance.ends_year}"
    return f"the end of {instance.ends_year}"


def temporary_text(instance: VirtueFlawInstance) -> str:
    """What the sheet says of a temporary Virtue or Flaw: "temporary,
    until Winter 1225", "temporary", or "" for a lasting one."""
    if not instance.temporary:
        return ""
    ends = ends_text(instance)
    return f"temporary, until {ends}" if ends else "temporary"


def _end_order(instance: VirtueFlawInstance) -> int | None:
    """The season it ends as a number (a year alone ends in its Winter)."""
    if not instance.temporary or instance.ends_year is None:
        return None
    season = instance.ends_season if instance.ends_season in SEASONS else SEASONS[-1]
    return season_order(season=season, year=instance.ends_year)


def ending(character: Character, year: int, season: str) -> list[int]:
    """The indices of the character's temporary Virtues and Flaws whose
    last season is `season` of `year`: they end as it passes."""
    now = season_order(season=season, year=year)
    return [
        index
        for index, vf in enumerate(character.virtues_flaws)
        if _end_order(vf) == now
    ]


def end_problem(
    year: int | None, season: str | None, now_year: int, now_season: str
) -> str:
    """Why an end season can't be kept ("" if it can): a season with no
    year, or one already past."""
    if year is None:
        return "Give the year it ends with its season." if season else ""
    order = season_order(season=season if season in SEASONS else SEASONS[-1], year=year)
    if order < season_order(season=now_season, year=now_year):
        return "It can't end in a season already past."
    return ""
